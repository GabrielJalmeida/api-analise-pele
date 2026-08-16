import os

from dotenv import load_dotenv


load_dotenv()


ORIGENS_CORS_PADRAO = [
    "http://localhost:5173",
]


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