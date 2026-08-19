from __future__ import annotations

import base64
import importlib
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from time import perf_counter
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError


MODELO_GEMINI = "gemini-3.5-flash-lite"
MODELO_OPENAI = "gpt-5.6-luna"
MODELO_ANTHROPIC = (
    "claude-haiku-4-5-20251001"
)

PROVEDOR_PADRAO = "gemini"

PROVEDORES_SUPORTADOS = {
    "gemini",
    "openai",
    "anthropic",
}

ALIASES_PROVEDORES = {
    "google": "gemini",
    "claude": "anthropic",
}

LOGGER = logging.getLogger(
    "uvicorn.error"
)

ModeloSaida = TypeVar(
    "ModeloSaida",
    bound=BaseModel,
)


class LimiteIAExcedido(Exception):
    pass


class ServicoIAIndisponivel(Exception):
    pass


class RespostaIAInvalida(Exception):
    pass


class ConfiguracaoIAInvalida(Exception):
    pass


@dataclass(frozen=True)
class ConfiguracaoProvedorIA:
    nome: str
    modelo: str
    api_key: str


def _obter_variavel(
    nome: str,
    padrao: str = "",
) -> str:
    return os.getenv(
        nome,
        padrao,
    ).strip()


def obter_provedor_ia() -> str:
    provedor = _obter_variavel(
        "AI_PROVIDER",
        PROVEDOR_PADRAO,
    ).lower()

    provedor = ALIASES_PROVEDORES.get(
        provedor,
        provedor,
    )

    if (
        provedor
        not in PROVEDORES_SUPORTADOS
    ):
        opcoes = ", ".join(
            sorted(
                PROVEDORES_SUPORTADOS
            )
        )

        raise ConfiguracaoIAInvalida(
            "AI_PROVIDER inválido. "
            f"Use uma destas opções: {opcoes}."
        )

    return provedor


def obter_modelo_gemini() -> str:
    return (
        _obter_variavel(
            "GEMINI_MODEL",
            MODELO_GEMINI,
        )
        or MODELO_GEMINI
    )


def obter_modelo_openai() -> str:
    return (
        _obter_variavel(
            "OPENAI_MODEL",
            MODELO_OPENAI,
        )
        or MODELO_OPENAI
    )


def obter_modelo_anthropic() -> str:
    return (
        _obter_variavel(
            "ANTHROPIC_MODEL",
            MODELO_ANTHROPIC,
        )
        or MODELO_ANTHROPIC
    )


def obter_configuracao_provedor(
) -> ConfiguracaoProvedorIA:
    provedor = obter_provedor_ia()

    configuracoes = {
        "gemini": (
            "GEMINI_API_KEY",
            obter_modelo_gemini(),
        ),
        "openai": (
            "OPENAI_API_KEY",
            obter_modelo_openai(),
        ),
        "anthropic": (
            "ANTHROPIC_API_KEY",
            obter_modelo_anthropic(),
        ),
    }

    nome_chave, modelo = (
        configuracoes[provedor]
    )

    api_key = _obter_variavel(
        nome_chave
    )

    if not api_key:
        raise ConfiguracaoIAInvalida(
            "A variável de ambiente "
            f"{nome_chave} não foi configurada."
        )

    return ConfiguracaoProvedorIA(
        nome=provedor,
        modelo=modelo,
        api_key=api_key,
    )


def _importar_sdk(
    modulo: str,
    pacote: str,
):
    try:
        return importlib.import_module(
            modulo
        )
    except ImportError as erro:
        raise ConfiguracaoIAInvalida(
            "O provedor selecionado exige "
            f"o pacote Python '{pacote}'."
        ) from erro


@lru_cache(maxsize=4)
def _criar_cliente_gemini(
    api_key: str,
):
    genai = _importar_sdk(
        "google.genai",
        "google-genai",
    )

    return genai.Client(
        api_key=api_key
    )


def obter_cliente_gemini():
    api_key = _obter_variavel(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise ConfiguracaoIAInvalida(
            "A variável de ambiente "
            "GEMINI_API_KEY não foi "
            "configurada."
        )

    return _criar_cliente_gemini(
        api_key
    )


@lru_cache(maxsize=4)
def _criar_cliente_openai(
    api_key: str,
):
    openai = _importar_sdk(
        "openai",
        "openai",
    )

    return openai.OpenAI(
        api_key=api_key,
        max_retries=2,
        timeout=75.0,
    )


@lru_cache(maxsize=4)
def _criar_cliente_anthropic(
    api_key: str,
):
    anthropic = _importar_sdk(
        "anthropic",
        "anthropic",
    )

    return anthropic.Anthropic(
        api_key=api_key,
        max_retries=2,
        timeout=75.0,
    )


def _obter_codigo_erro(
    erro: Exception,
) -> int | None:
    for atributo in (
        "status_code",
        "code",
    ):
        valor = getattr(
            erro,
            atributo,
            None,
        )

        if isinstance(valor, int):
            return valor

    resposta = getattr(
        erro,
        "response",
        None,
    )

    valor = getattr(
        resposta,
        "status_code",
        None,
    )

    if isinstance(valor, int):
        return valor

    return None


def _converter_erro_provedor(
    erro: Exception,
) -> Exception:
    if isinstance(
        erro,
        (
            LimiteIAExcedido,
            ServicoIAIndisponivel,
            RespostaIAInvalida,
            ConfiguracaoIAInvalida,
        ),
    ):
        return erro

    if isinstance(
        erro,
        ValidationError,
    ):
        return RespostaIAInvalida()

    codigo = _obter_codigo_erro(
        erro
    )

    nome_erro = (
        type(erro).__name__.lower()
    )

    if (
        codigo == 429
        or "ratelimit" in nome_erro
        or "rate_limit" in nome_erro
    ):
        return LimiteIAExcedido()

    if codigo in {
        400,
        401,
        403,
        404,
        422,
    }:
        return ConfiguracaoIAInvalida()

    if (
        codigo is not None
        and codigo >= 500
    ):
        return ServicoIAIndisponivel()

    if any(
        termo in nome_erro
        for termo in (
            "connection",
            "timeout",
            "server",
            "overloaded",
        )
    ):
        return ServicoIAIndisponivel()

    return ServicoIAIndisponivel()


def _validar_resultado(
    valor: Any,
    modelo_saida: type[ModeloSaida],
) -> ModeloSaida:
    try:
        if isinstance(
            valor,
            modelo_saida,
        ):
            return valor

        if isinstance(valor, str):
            return (
                modelo_saida
                .model_validate_json(
                    valor
                )
            )

        return modelo_saida.model_validate(
            valor
        )
    except (
        TypeError,
        ValidationError,
    ) as erro:
        raise RespostaIAInvalida from erro


def _executar_gemini(
    configuracao: ConfiguracaoProvedorIA,
    prompt: str,
    modelo_saida: type[ModeloSaida],
    conteudo_imagem: bytes | None,
    mime_type: str | None,
) -> ModeloSaida:
    cliente = _criar_cliente_gemini(
        configuracao.api_key
    )

    if conteudo_imagem is None:
        entrada: Any = prompt
    else:
        entrada = [
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "image",
                "data": base64.b64encode(
                    conteudo_imagem
                ).decode("utf-8"),
                "mime_type": mime_type,
            },
        ]

    interaction = (
        cliente.interactions.create(
            model=configuracao.modelo,
            input=entrada,
            store=False,
            response_format={
                "type": "text",
                "mime_type": (
                    "application/json"
                ),
                "schema": (
                    modelo_saida
                    .model_json_schema()
                ),
            },
        )
    )

    return _validar_resultado(
        interaction.output_text,
        modelo_saida,
    )


def _executar_openai(
    configuracao: ConfiguracaoProvedorIA,
    prompt: str,
    modelo_saida: type[ModeloSaida],
    conteudo_imagem: bytes | None,
    mime_type: str | None,
) -> ModeloSaida:
    cliente = _criar_cliente_openai(
        configuracao.api_key
    )

    if conteudo_imagem is None:
        entrada: Any = prompt
    else:
        imagem_base64 = base64.b64encode(
            conteudo_imagem
        ).decode("utf-8")

        entrada = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            f"data:{mime_type};"
                            "base64,"
                            f"{imagem_base64}"
                        ),
                        "detail": "high",
                    },
                ],
            }
        ]

    resposta = cliente.responses.parse(
        model=configuracao.modelo,
        input=entrada,
        text_format=modelo_saida,
        store=False,
    )

    return _validar_resultado(
        resposta.output_parsed,
        modelo_saida,
    )


def _executar_anthropic(
    configuracao: ConfiguracaoProvedorIA,
    prompt: str,
    modelo_saida: type[ModeloSaida],
    conteudo_imagem: bytes | None,
    mime_type: str | None,
) -> ModeloSaida:
    cliente = (
        _criar_cliente_anthropic(
            configuracao.api_key
        )
    )

    if conteudo_imagem is None:
        conteudo: Any = prompt
    else:
        conteudo = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": base64.b64encode(
                        conteudo_imagem
                    ).decode("utf-8"),
                },
            },
            {
                "type": "text",
                "text": prompt,
            },
        ]

    resposta = cliente.messages.parse(
        model=configuracao.modelo,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": conteudo,
            }
        ],
        output_format=modelo_saida,
    )

    return _validar_resultado(
        resposta.parsed_output,
        modelo_saida,
    )


def executar_analise_estruturada(
    prompt: str,
    modelo_saida: type[ModeloSaida],
    *,
    operacao: str,
    conteudo_imagem: bytes | None = None,
    mime_type: str | None = None,
) -> ModeloSaida:
    configuracao = (
        obter_configuracao_provedor()
    )

    if (
        conteudo_imagem is not None
        and not mime_type
    ):
        raise ConfiguracaoIAInvalida(
            "O tipo da imagem não foi "
            "informado."
        )

    executores = {
        "gemini": _executar_gemini,
        "openai": _executar_openai,
        "anthropic": (
            _executar_anthropic
        ),
    }

    inicio = perf_counter()

    try:
        resultado = executores[
            configuracao.nome
        ](
            configuracao,
            prompt,
            modelo_saida,
            conteudo_imagem,
            mime_type,
        )
    except Exception as erro:
        erro_convertido = (
            _converter_erro_provedor(
                erro
            )
        )

        LOGGER.warning(
            "ai_request_failed provider=%s "
            "operation=%s model=%s error_type=%s "
            "code=%s "
            "input_bytes=%s duration_ms=%.1f",
            configuracao.nome,
            operacao,
            configuracao.modelo,
            type(erro).__name__,
            _obter_codigo_erro(erro),
            (
                len(conteudo_imagem)
                if conteudo_imagem
                is not None
                else 0
            ),
            (
                perf_counter() - inicio
            ) * 1000,
        )

        if erro_convertido is erro:
            raise

        raise erro_convertido from erro

    LOGGER.info(
        "ai_request_completed provider=%s "
        "operation=%s model=%s "
        "input_bytes=%s duration_ms=%.1f",
        configuracao.nome,
        operacao,
        configuracao.modelo,
        (
            len(conteudo_imagem)
            if conteudo_imagem is not None
            else 0
        ),
        (
            perf_counter() - inicio
        ) * 1000,
    )

    return resultado
