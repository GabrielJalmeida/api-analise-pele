import os

from dotenv import set_key

from ai_providers import (
    obter_modelo_anthropic,
    obter_modelo_gemini,
    obter_modelo_openai,
    obter_provedor_ia,
)
from config import (
    ambiente_desktop,
    obter_diretorio_dados,
    pedidos_atualizam_estoque,
)
from models import ConfiguracaoIAEntrada


CHAVES_PROVEDORES = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}

MODELOS_PROVEDORES = {
    "gemini": "GEMINI_MODEL",
    "openai": "OPENAI_MODEL",
    "anthropic": "ANTHROPIC_MODEL",
}


def _modelo_atual(provedor: str) -> str:
    return {
        "gemini": obter_modelo_gemini,
        "openai": obter_modelo_openai,
        "anthropic": obter_modelo_anthropic,
    }[provedor]()


def _caminho_configuracao():
    diretorio = obter_diretorio_dados()

    if diretorio is None:
        return None

    caminho = diretorio / "config" / ".env"
    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    caminho.touch(exist_ok=True)
    return caminho


def obter_configuracao_ia() -> dict:
    provedor = obter_provedor_ia()

    return {
        "provedor": provedor,
        "modelo": _modelo_atual(provedor),
        "api_key_configurada": bool(
            os.getenv(
                CHAVES_PROVEDORES[provedor],
                "",
            ).strip()
        ),
        "pedidos_atualizam_estoque": (
            pedidos_atualizam_estoque()
        ),
        "armazenamento": (
            "arquivo_local"
            if ambiente_desktop()
            else "variaveis_de_ambiente"
        ),
    }


def salvar_configuracao_ia(
    dados: ConfiguracaoIAEntrada,
) -> dict:
    caminho = _caminho_configuracao()

    if not ambiente_desktop() or caminho is None:
        raise RuntimeError(
            "No modo de desenvolvimento, configure a IA pelo arquivo .env"
        )

    valores = {
        "AI_PROVIDER": dados.provedor,
        MODELOS_PROVEDORES[dados.provedor]: dados.modelo,
        "PEDIDOS_ATUALIZAM_ESTOQUE": (
            "true"
            if dados.pedidos_atualizam_estoque
            else "false"
        ),
    }

    if dados.api_key:
        valores[
            CHAVES_PROVEDORES[dados.provedor]
        ] = dados.api_key

    for chave, valor in valores.items():
        os.environ[chave] = valor
        set_key(
            str(caminho),
            chave,
            valor,
            quote_mode="always",
        )

    return obter_configuracao_ia()
