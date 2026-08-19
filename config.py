import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


ORIGENS_CORS_PADRAO = [
    "http://localhost:5173",
    "http://localhost:5174",
]

CAMINHO_BANCO_PADRAO = (
    Path(__file__).resolve().parent
    / "produtos.db"
)

DIRETORIO_MEDIA_PADRAO = (
    Path(__file__).resolve().parent
    / "media"
)

VERSAO_APLICACAO = "X"


def obter_diretorio_dados() -> Path | None:
    diretorio_configurado = os.getenv(
        "LUMINA_DATA_DIR",
        "",
    ).strip()

    if not diretorio_configurado:
        return None

    return Path(diretorio_configurado)


def obter_caminho_banco() -> Path:
    caminho_configurado = os.getenv(
        "DATABASE_PATH",
        "",
    ).strip()

    if caminho_configurado:
        return Path(caminho_configurado)

    diretorio_dados = obter_diretorio_dados()

    if diretorio_dados is not None:
        return (
            diretorio_dados
            / "data"
            / "produtos.db"
        )

    return CAMINHO_BANCO_PADRAO


def obter_diretorio_media() -> Path:
    caminho_configurado = os.getenv(
        "MEDIA_PATH",
        "",
    ).strip()

    if caminho_configurado:
        return Path(caminho_configurado)

    diretorio_dados = obter_diretorio_dados()

    if diretorio_dados is not None:
        return diretorio_dados / "media"

    return DIRETORIO_MEDIA_PADRAO


def ambiente_producao() -> bool:
    return (
        os.getenv("APP_ENV", "development")
        .strip()
        .lower()
        == "production"
    )


def ambiente_desktop() -> bool:
    return (
        os.getenv("APP_ENV", "development")
        .strip()
        .lower()
        == "desktop"
    )


def pedidos_atualizam_estoque() -> bool:
    valor = os.getenv(
        "PEDIDOS_ATUALIZAM_ESTOQUE",
        "false",
    ).strip().lower()

    return valor in {
        "1",
        "true",
        "sim",
        "yes",
        "on",
    }


def obter_origens_cors() -> list[str]:
    origens_configuradas = os.getenv(
        "CORS_ORIGINS",
        "",
    ).strip()

    if not origens_configuradas:
        return ORIGENS_CORS_PADRAO.copy()

    return [
        origem.strip()
        for origem in origens_configuradas.split(",")
        if origem.strip()
    ]
