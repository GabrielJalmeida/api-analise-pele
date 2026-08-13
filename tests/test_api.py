from io import BytesIO

from PIL import Image

import main
from models import ResultadoAnaliseFoto, ResultadoAnaliseIA


def criar_imagem_jpeg():
    arquivo = BytesIO()
    Image.new("RGB", (100, 100), color=(210, 180, 160)).save(
        arquivo,
        format="JPEG",
    )
    return arquivo.getvalue()


def criar_png_acima_de_vinte_megapixels():
    arquivo = BytesIO()
    Image.new("1", (5000, 4001), color=0).save(arquivo, format="PNG")
    return arquivo.getvalue()


def test_api_inicia_e_rotas_sem_ia_funcionam_sem_chave(client, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    resposta = client.get("/status")

    assert resposta.status_code == 200
    assert resposta.json()["projeto"] == "Análise de Pele para Loja de cosméticos"


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


def test_analise_por_texto_nao_depende_de_foto(client, monkeypatch):
    monkeypatch.setattr(
        main,
        "interpretar_perfil",
        lambda texto: ResultadoAnaliseIA(
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


def test_analise_por_foto_nao_depende_de_texto(client, monkeypatch):
    monkeypatch.setattr(
        main,
        "interpretar_foto",
        lambda conteudo, mime_type: ResultadoAnaliseFoto(
            imagem_adequada=True,
            tipo_pele="normal",
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
                b"0" * (main.TAMANHO_MAXIMO_IMAGEM + 1),
                "image/jpeg",
            )
        },
    )

    assert resposta.status_code == 413


def test_upload_rejeita_imagem_acima_de_vinte_megapixels(client):
    resposta = client.post(
        "/analise-foto",
        files={
            "arquivo": (
                "dimensoes-grandes.png",
                criar_png_acima_de_vinte_megapixels(),
                "image/png",
            )
        },
    )

    assert resposta.status_code == 413
