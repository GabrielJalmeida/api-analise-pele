from io import BytesIO

from PIL import Image

import routers.analise as router_analise
from models import ResultadoAnaliseFoto, ResultadoAnaliseIA


def criar_imagem_jpeg():
    arquivo = BytesIO()
    Image.new("RGB", (100, 100), color=(210, 180, 160)).save(
        arquivo,
        format="JPEG",
    )
    return arquivo.getvalue()


def criar_png_acima_de_cinquenta_megapixels():
    arquivo = BytesIO()

    Image.new(
        "1",
        (8000, 6251),
        color=0,
    ).save(
        arquivo,
        format="PNG",
    )

    return arquivo.getvalue()


def test_api_inicia_e_rotas_sem_ia_funcionam_sem_chave(client, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    resposta = client.get("/status")

    assert resposta.status_code == 200
    assert resposta.json()["projeto"] == "Análise de Pele para Loja de cosméticos"
    assert resposta.json()["versao"] == "4.0.0"


def test_rota_de_ia_sem_chave_retorna_indisponibilidade(client, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    resposta = client.post(
        "/analise-texto",
        json={"texto": "Minha pele fica oleosa durante o dia."},
    )

    assert resposta.status_code == 503
    assert resposta.json()["status"] == "servico_ia_indisponivel"


def test_crud_basico_e_recomendacao(client, produto_valido):
    criacao = client.post("/produto", json=produto_valido)
    duplicado = client.post("/produto", json=produto_valido)
    listagem = client.get("/produtos")
    atualizacao = client.patch(
        f"/produto/{criacao.json()['id']}",
        json={"preco": 44.90},
    )
    recomendacoes = client.post(
        "/recomendacoes",
        json={
            "tipo_pele": "oleosa",
            "sensivel": True,
            "tem_espinha": True,
        },
    )

    assert criacao.status_code == 200
    assert duplicado.status_code == 409
    assert listagem.status_code == 200
    assert len(listagem.json()) == 1
    assert atualizacao.status_code == 200
    assert atualizacao.json()["preco"] == 44.90
    assert recomendacoes.status_code == 200
    assert recomendacoes.json()["total_recomendacoes"] == 1
    assert recomendacoes.json()["recomendacoes"]["limpeza"][0]["score"] == 7


def test_escrita_administrativa_eh_bloqueada_em_producao(
    client,
    produto_valido,
    monkeypatch,
):
    monkeypatch.setenv("APP_ENV", "production")

    criacao = client.post(
        "/produto",
        json=produto_valido,
    )
    listagem = client.get("/produtos")

    assert criacao.status_code == 404
    assert criacao.json()["detail"] == (
        "Rota não disponível neste ambiente"
    )
    assert listagem.status_code == 200


def test_analise_por_texto_nao_depende_de_foto(client, monkeypatch):
    monkeypatch.setattr(
        router_analise,
        "interpretar_perfil",
        lambda texto: ResultadoAnaliseIA(
    entrada_valida=True,
    motivo_invalidacao=None,
    tipo_pele="seca",
    sensivel=True,
    tem_espinha=False,
),
    )

    resposta = client.post(
        "/analise-texto",
        json={"texto": "Minha pele resseca e costuma ficar sensível."},
    )

    assert resposta.status_code == 200
    assert resposta.json()["perfil"]["tipo_pele"] == "seca"


def test_analise_por_foto_nao_depende_de_texto(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        router_analise,
        "interpretar_foto",
        lambda conteudo, mime_type: ResultadoAnaliseFoto(
            imagem_adequada=True,
            tipo_pele="normal",
            confianca_tipo_pele="alta",
            tem_espinha=False,
        ),
    )

    resposta = client.post(
        "/analise-foto",
        files={
            "arquivo": (
                "pele.jpg",
                criar_imagem_jpeg(),
                "image/jpeg",
            )
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "sucesso"
    assert resposta.json()["analise"]["tipo_pele"] == "normal"


def test_upload_rejeita_arquivo_que_nao_eh_imagem(client):
    resposta = client.post(
        "/analise-foto",
        files={"arquivo": ("falso.jpg", b"nao sou imagem", "image/jpeg")},
    )

    assert resposta.status_code == 415


def test_upload_rejeita_arquivo_acima_de_cinco_megabytes(client):
    resposta = client.post(
        "/analise-foto",
        files={
            "arquivo": (
                "grande.jpg",
                b"0" * (router_analise.TAMANHO_MAXIMO_IMAGEM + 1),
                "image/jpeg",
            )
        },
    )

    assert resposta.status_code == 413


def test_upload_rejeita_imagem_acima_de_cinquenta_megapixels(client):
    resposta = client.post(
        "/analise-foto",
        files={
            "arquivo": (
                "dimensoes-grandes.png",
                criar_png_acima_de_cinquenta_megapixels(),
                "image/png",
            )
        },
    )

    assert resposta.status_code == 413

def test_rota_raiz_confirma_funcionamento(client):
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "message": "A API está funcionando!"
    }


def test_resposta_inclui_dados_de_rastreamento(
    client,
):
    resposta = client.get("/status")

    assert resposta.status_code == 200
    assert resposta.headers[
        "x-request-id"
    ]
    assert resposta.headers[
        "server-timing"
    ].startswith("app;dur=")

def test_analise_texto_retorna_informacoes_insuficientes(
    client,
    monkeypatch
):
    monkeypatch.setattr(
        router_analise,
        "interpretar_perfil",
        lambda texto: ResultadoAnaliseIA(
    entrada_valida=True,
    motivo_invalidacao=None,
    tipo_pele=None,
    sensivel=None,
    tem_espinha=None,
),
    )

    resposta = client.post(
        "/analise-texto",
        json={
            "texto": "Quero alguns produtos para cuidar melhor do meu rosto."
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "informacoes_insuficientes"
    assert resposta.json()["total_recomendacoes"] == 0
    assert resposta.json()["recomendacoes"] == {}

def test_analise_foto_retorna_imagem_inadequada(
    client,
    monkeypatch
):
    monkeypatch.setattr(
        router_analise,
        "interpretar_foto",
        lambda conteudo, mime_type: ResultadoAnaliseFoto(
            imagem_adequada=False,
            motivo_inadequacao="pele_molhada",
        ),
    )

    resposta = client.post(
        "/analise-foto",
        files={
            "arquivo": (
                "pele.jpg",
                criar_imagem_jpeg(),
                "image/jpeg",
            )
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "imagem_inadequada"
    assert resposta.json()["analise"]["imagem_adequada"] is False
    assert resposta.json()["analise"]["motivo_inadequacao"] == "pele_molhada"

def test_analise_foto_retorna_informacoes_insuficientes(
    client,
    monkeypatch
):
    monkeypatch.setattr(
        router_analise,
        "interpretar_foto",
        lambda conteudo, mime_type: ResultadoAnaliseFoto(
            imagem_adequada=True,
            tipo_pele=None,
            tem_espinha=None,
        ),
    )

    resposta = client.post(
        "/analise-foto",
        files={
            "arquivo": (
                "pele.jpg",
                criar_imagem_jpeg(),
                "image/jpeg",
            )
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "informacoes_insuficientes"
    assert resposta.json()["total_recomendacoes"] == 0
    assert resposta.json()["recomendacoes"] == {}
    assert "área visível" in (
        resposta.json()["mensagem"].lower()
    )

def test_listagem_de_produtos_aceita_filtros(client, produto_valido):
    client.post("/produto", json=produto_valido)

    hidratante = {
        **produto_valido,
        "nome": "Hidratante universal teste",
        "categoria": "hidratante",
        "tipo_pele": "todos",
    }

    inativo = {
        **produto_valido,
        "nome": "Serum inativo teste",
        "categoria": "serum",
        "tipo_pele": "seca",
        "ativo": False,
    }

    client.post("/produto", json=hidratante)
    client.post("/produto", json=inativo)

    por_categoria = client.get(
        "/produtos",
        params={"categoria": "limpeza"},
    )

    por_tipo = client.get(
        "/produtos",
        params={"tipo_pele": "todos"},
    )

    por_status = client.get(
        "/produtos",
        params={"ativo": False},
    )

    por_busca = client.get(
        "/produtos",
        params={"busca": "Gel"},
    )

    assert por_categoria.status_code == 200
    assert len(por_categoria.json()) == 1
    assert por_categoria.json()[0]["categoria"] == "limpeza"

    assert len(por_tipo.json()) == 1
    assert por_tipo.json()[0]["tipo_pele"] == "todos"

    assert len(por_status.json()) == 1
    assert por_status.json()[0]["ativo"] is False

    assert len(por_busca.json()) == 1
    assert por_busca.json()[0]["nome"] == produto_valido["nome"]

def test_desativacao_de_produto_preserva_registro_e_remove_das_recomendacoes(
    client,
    produto_valido,
):
    criacao = client.post("/produto", json=produto_valido)
    id_produto = criacao.json()["id"]

    desativacao = client.delete(f"/produto/{id_produto}")

    consulta = client.get(f"/produto/{id_produto}")

    recomendacoes = client.post(
        "/recomendacoes",
        json={
            "tipo_pele": "oleosa",
            "sensivel": True,
            "tem_espinha": True,
        },
    )

    segunda_desativacao = client.delete(f"/produto/{id_produto}")

    assert desativacao.status_code == 200
    assert desativacao.json()["status"] == "produto_desativado"

    assert consulta.status_code == 200
    assert consulta.json()["ativo"] is False

    assert recomendacoes.status_code == 200
    assert recomendacoes.json()["total_recomendacoes"] == 0

    assert segunda_desativacao.status_code == 409

def test_erro_de_validacao_tem_formato_padronizado(client):
    resposta = client.post(
        "/recomendacoes",
        json={
            "tipo_pele": "tipo_inexistente",
            "sensivel": True,
            "tem_espinha": False,
        },
    )

    assert resposta.status_code == 422

    dados = resposta.json()

    assert dados["status"] == "dados_invalidos"
    assert dados["mensagem"] == "Os dados enviados são inválidos."
    assert dados["erros"][0]["campo"] == "tipo_pele"
    assert dados["erros"][0]["mensagem"] == "Valor inválido."

def test_analise_texto_rejeita_sujeito_nao_humano(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        router_analise,
        "interpretar_perfil",
        lambda texto: ResultadoAnaliseIA(
            entrada_valida=False,
            motivo_invalidacao="sujeito_nao_humano",
            tipo_pele=None,
            sensivel=None,
            tem_espinha=None,
        ),
    )

    resposta = client.post(
        "/analise-texto",
        json={
            "texto": (
                "Eu sou um robô e minha lataria "
                "vaza óleo constantemente."
            )
        },
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["status"] == "fora_escopo"
    assert dados["motivo"] == "sujeito_nao_humano"

    assert "perfil" not in dados
    assert "recomendacoes" not in dados

def test_analise_texto_rejeita_pele_artificial(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        router_analise,
        "interpretar_perfil",
        lambda texto: ResultadoAnaliseIA(
            entrada_valida=False,
            motivo_invalidacao="fora_do_dominio",
            tipo_pele=None,
            sensivel=None,
            tem_espinha=None,
        ),
    )

    resposta = client.post(
        "/analise-texto",
        json={
            "texto": (
                "Sou uma pessoa e utilizo pele artificial. "
                "Preciso de algo para mantê-la hidratada."
            )
        },
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["status"] == "fora_escopo"
    assert dados["motivo"] == "fora_do_dominio"

    assert "perfil" not in dados
    assert "recomendacoes" not in dados

def test_analise_foto_com_texto_divergente_exige_confirmacao(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        router_analise,
        "interpretar_foto",
        lambda conteudo, mime_type: ResultadoAnaliseFoto(
            imagem_adequada=True,
            tipo_pele="seca",
            confianca_tipo_pele="alta",
            tem_espinha=True,
            marcas_pos_acne=None,
            vermelhidao=None,
            descamacao=True,
            brilho_excessivo=False,
        ),
    )

    monkeypatch.setattr(
        router_analise,
        "interpretar_perfil",
        lambda texto: ResultadoAnaliseIA(
            entrada_valida=True,
            motivo_invalidacao=None,
            tipo_pele="mista",
            sensivel=True,
            tem_espinha=None,
        ),
    )

    resposta = client.post(
        "/analise-foto",
        files={
            "arquivo": (
                "pele.jpg",
                criar_imagem_jpeg(),
                "image/jpeg",
            ),
        },
        data={
            "texto": (
                "Minha testa fica oleosa durante o dia, "
                "mas minhas bochechas costumam ressecar."
            ),
        },
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["status"] == "confirmacao_necessaria"

    assert dados["sensivel"] is True
    assert dados["tem_espinha"] is True

    assert dados["analise"]["tipo_pele"] == "seca"

    assert "perfil" not in dados
    assert "recomendacoes" not in dados

def test_analise_foto_com_texto_compativel_combina_as_fontes(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        router_analise,
        "interpretar_foto",
        lambda conteudo, mime_type: ResultadoAnaliseFoto(
            imagem_adequada=True,
            tipo_pele="mista",
            confianca_tipo_pele="alta",
            tem_espinha=True,
            marcas_pos_acne=None,
            vermelhidao=None,
            descamacao=False,
            brilho_excessivo=True,
        ),
    )

    monkeypatch.setattr(
        router_analise,
        "interpretar_perfil",
        lambda texto: ResultadoAnaliseIA(
            entrada_valida=True,
            motivo_invalidacao=None,
            tipo_pele="mista",
            sensivel=True,
            tem_espinha=None,
        ),
    )

    resposta = client.post(
        "/analise-foto",
        files={
            "arquivo": (
                "pele.jpg",
                criar_imagem_jpeg(),
                "image/jpeg",
            ),
        },
        data={
            "texto": (
                "Minha zona T costuma ficar oleosa, "
                "mas minhas bochechas são mais secas."
            ),
        },
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["status"] == "sucesso"

    assert dados["perfil"]["tipo_pele"] == "mista"
    assert dados["perfil"]["sensivel"] is True

    # O texto não informou espinhas,
    # então aproveitamos a observação da foto.
    assert dados["perfil"]["tem_espinha"] is True

    # A análise visual continua preservada.
    assert dados["analise"]["tipo_pele"] == "mista"
