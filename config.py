import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


ORIGENS_CORS_PADRAO = [
    "http://localhost:5173",
]

CAMINHO_BANCO_PADRAO = (
    Path(__file__).resolve().parent
    / "produtos.db"
)


def obter_caminho_banco() -> Path:
    caminho_configurado = os.getenv(
        "DATABASE_PATH",
        "",
    ).strip()

    if caminho_configurado:
        return Path(caminho_configurado)

    return CAMINHO_BANCO_PADRAO


def ambiente_producao() -> bool:
    return (
        os.getenv("APP_ENV", "development")
        .strip()
        .lower()
        == "production"
    )


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