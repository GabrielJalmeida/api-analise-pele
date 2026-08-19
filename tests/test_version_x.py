import hashlib
from datetime import datetime, timedelta, timezone
from io import BytesIO

from openpyxl import Workbook
from PIL import Image

import database
import product_image_service
import routers.importacao as router_importacao
from models import CatalogoInterpretado, ProdutoImportacaoRascunho


TOKEN_CLIENTE = "cliente-teste-1234567890-abcdefghi"


def _imagem_produto() -> bytes:
    arquivo = BytesIO()
    Image.new(
        "RGB",
        (80, 80),
        "white",
    ).save(arquivo, format="JPEG")
    return arquivo.getvalue()


def _pedido(produto_id: int) -> dict:
    return {
        "cliente_token": TOKEN_CLIENTE,
        "cliente_nome": "Pessoa Teste",
        "cliente_email": "pessoa@example.com",
        "consentimento_retencao": True,
        "itens": [
            {
                "produto_id": produto_id,
                "quantidade": 2,
            }
        ],
    }


def test_produto_aceita_campos_descritivos_ausentes(client):
    resposta = client.post(
        "/produto",
        json={
            "nome": "Produto essencial",
            "preco": 29.9,
            "categoria": "outros",
            "tipo_pele": "todos",
        },
    )

    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["marca"] == ""
    assert dados["descricao_curta"] == ""
    assert dados["imagem_url"] == ""
    assert dados["conteudo"] == ""
    assert dados["ativos_principais"] == ""
    assert dados["estoque"] == 0


def test_imagem_orfa_pode_ser_removida_mas_imagem_em_uso_nao(
    client,
    monkeypatch,
    tmp_path,
):
    pasta_imagens = tmp_path / "media" / "produtos"
    monkeypatch.setattr(
        product_image_service,
        "MEDIA_PRODUTOS_DIR",
        pasta_imagens,
    )

    upload = client.post(
        "/produtos/imagem",
        data={
            "nome_produto": "Produto com foto",
            "categoria": "outros",
        },
        files={
            "arquivo": (
                "produto.jpg",
                _imagem_produto(),
                "image/jpeg",
            )
        },
    )

    assert upload.status_code == 201
    imagem_url = upload.json()["imagem_url"]
    imagem_salva = (
        pasta_imagens
        / "outros"
        / imagem_url.rsplit("/", 1)[-1]
    )
    assert imagem_salva.is_file()

    removida = client.delete(
        "/produtos/imagem",
        params={"imagem_url": imagem_url},
    )
    assert removida.status_code == 204
    assert not imagem_salva.exists()

    outro_upload = client.post(
        "/produtos/imagem",
        data={
            "nome_produto": "Produto vinculado",
            "categoria": "outros",
        },
        files={
            "arquivo": (
                "produto.jpg",
                _imagem_produto(),
                "image/jpeg",
            )
        },
    )
    outra_url = outro_upload.json()["imagem_url"]

    produto = client.post(
        "/produto",
        json={
            "nome": "Produto vinculado",
            "preco": 19.9,
            "categoria": "outros",
            "tipo_pele": "todos",
            "imagem_url": outra_url,
        },
    )
    assert produto.status_code == 200

    protegida = client.delete(
        "/produtos/imagem",
        params={"imagem_url": outra_url},
    )
    assert protegida.status_code == 409


def test_pedido_usa_preco_do_banco_e_guarda_token_com_hash(
    client,
    produto_valido,
):
    produto = client.post(
        "/produto",
        json=produto_valido,
    ).json()

    resposta = client.post(
        "/pedidos",
        json=_pedido(produto["id"]),
    )

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["status"] == "pedido_registrado"
    assert dados["pedido"]["modo"] == "demonstracao"
    assert dados["pedido"]["total"] == 79.8
    assert dados["pedido"]["itens"][0]["preco_unitario"] == 39.9

    with database.gerenciar_banco() as (_, cursor):
        cursor.execute(
            "SELECT cliente_token_hash FROM pedidos"
        )
        token_salvo = cursor.fetchone()[0]

    assert token_salvo != TOKEN_CLIENTE
    assert token_salvo == hashlib.sha256(
        TOKEN_CLIENTE.encode("utf-8")
    ).hexdigest()

    produto_depois = client.get(
        f"/produto/{produto['id']}"
    ).json()
    assert produto_depois["estoque"] == 10


def test_historico_isolado_expira_e_pode_ser_excluido(
    client,
    produto_valido,
):
    produto = client.post(
        "/produto",
        json=produto_valido,
    ).json()
    client.post(
        "/pedidos",
        json=_pedido(produto["id"]),
    )

    historico = client.get(
        "/pedidos/historico",
        headers={"X-Cliente-Token": TOKEN_CLIENTE},
    )
    outro_historico = client.get(
        "/pedidos/historico",
        headers={
            "X-Cliente-Token": "outro-cliente-1234567890-abcdefghij"
        },
    )

    assert historico.status_code == 200
    assert historico.json()["retencao_dias"] == 365
    assert historico.json()["total"] == 1
    assert outro_historico.json()["total"] == 0

    exclusao = client.delete(
        "/pedidos/historico",
        headers={"X-Cliente-Token": TOKEN_CLIENTE},
    )
    assert exclusao.json()["pedidos_removidos"] == 1

    expirado = (
        datetime.now(timezone.utc)
        - timedelta(seconds=1)
    ).isoformat(timespec="seconds")

    client.post(
        "/pedidos",
        json=_pedido(produto["id"]),
    )

    with database.gerenciar_transacao() as (_, cursor):
        cursor.execute(
            "UPDATE pedidos SET expira_em = ?",
            (expirado,),
        )

    depois_expiracao = client.get(
        "/pedidos/historico",
        headers={"X-Cliente-Token": TOKEN_CLIENTE},
    )
    assert depois_expiracao.json()["total"] == 0


def test_pedido_rejeita_produto_sem_estoque(client):
    produto = client.post(
        "/produto",
        json={
            "nome": "Sem estoque",
            "preco": 10,
            "categoria": "outros",
            "tipo_pele": "todos",
        },
    ).json()

    resposta = client.post(
        "/pedidos",
        json=_pedido(produto["id"]),
    )
    assert resposta.status_code == 409
    assert "Estoque insuficiente" in resposta.json()["detail"]


def test_importacao_csv_cria_previa_e_confirma(client):
    csv = (
        "produto;valor;quantidade;categoria;tipo de pele;marca\n"
        "Gel suave;R$ 35,90;12;limpeza;oleosa;Marca A\n"
        "Linha incompleta;;;limpeza;;\n"
    ).encode("utf-8")

    previa = client.post(
        "/produtos/importacao/arquivo",
        files={
            "arquivo": (
                "catalogo.csv",
                csv,
                "text/csv",
            )
        },
    )

    assert previa.status_code == 200
    dados = previa.json()
    assert dados["total_linhas"] == 2
    assert dados["total_validos"] == 1
    assert dados["total_erros"] >= 1
    assert dados["produtos"][0]["preco"] == 35.9

    confirmacao = client.post(
        "/produtos/importacao/confirmar",
        json={
            "produtos": dados["produtos"],
            "duplicados": "ignorar",
        },
    )
    assert confirmacao.status_code == 200
    assert confirmacao.json()["criados"] == 1


def test_importacao_xlsx_e_atualizacao_de_duplicado(client):
    pasta = Workbook()
    planilha = pasta.active
    planilha.append(
        ["Nome", "Preço", "Categoria", "Tipo de pele", "Estoque"]
    )
    planilha.append(
        ["Hidratante leve", 42.5, "hidratante", "todos", 8]
    )
    arquivo = BytesIO()
    pasta.save(arquivo)

    previa = client.post(
        "/produtos/importacao/arquivo",
        files={
            "arquivo": (
                "catalogo.xlsx",
                arquivo.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    ).json()

    produto = previa["produtos"][0]
    primeira = client.post(
        "/produtos/importacao/confirmar",
        json={"produtos": [produto]},
    )
    produto["preco"] = 51.0
    segunda = client.post(
        "/produtos/importacao/confirmar",
        json={
            "produtos": [produto],
            "duplicados": "atualizar",
        },
    )

    assert primeira.json()["criados"] == 1
    assert segunda.json()["atualizados"] == 1
    assert client.get("/produtos").json()[0]["preco"] == 51.0


def test_importacao_ia_sempre_retorna_previa(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        router_importacao,
        "interpretar_catalogo",
        lambda texto: CatalogoInterpretado(
            produtos=[
                ProdutoImportacaoRascunho(
                    nome="Sérum organizado",
                    preco=59.9,
                    estoque=4,
                    categoria="serum",
                    tipo_pele="mista",
                )
            ]
        ),
    )

    previa = client.post(
        "/produtos/importacao/ia",
        json={
            "texto": "serum organizado 59,90 mista estoque 4"
        },
    )

    assert previa.status_code == 200
    assert previa.json()["status"] == "previa_pronta"
    assert previa.json()["origem"] == "ia"
    assert previa.json()["total_validos"] == 1
    assert client.get("/produtos").json() == []


def test_configuracao_desktop_salva_provedor_sem_expor_chave(
    client,
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv("APP_ENV", "desktop")
    monkeypatch.setenv("LUMINA_DATA_DIR", str(tmp_path))

    resposta = client.put(
        "/admin/configuracao/ia",
        json={
            "provedor": "openai",
            "modelo": "gpt-modelo-teste",
            "api_key": "chave-local-teste-123456",
            "pedidos_atualizam_estoque": True,
        },
    )

    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["provedor"] == "openai"
    assert dados["modelo"] == "gpt-modelo-teste"
    assert dados["api_key_configurada"] is True
    assert dados["pedidos_atualizam_estoque"] is True
    assert "api_key" not in dados

    arquivo = tmp_path / "config" / ".env"
    assert arquivo.is_file()
    assert "OPENAI_API_KEY" in arquivo.read_text(
        encoding="utf-8"
    )


def test_configuracao_nao_grava_arquivo_fora_do_desktop(
    client,
    monkeypatch,
):
    monkeypatch.setenv("APP_ENV", "development")

    resposta = client.put(
        "/admin/configuracao/ia",
        json={
            "provedor": "gemini",
            "modelo": "gemini-modelo-teste",
            "api_key": "chave-de-teste-segura",
            "pedidos_atualizam_estoque": False,
        },
    )

    assert resposta.status_code == 409
    assert "arquivo .env" in resposta.json()["detail"]
