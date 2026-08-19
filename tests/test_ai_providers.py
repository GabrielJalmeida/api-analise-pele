from types import SimpleNamespace

import ai_providers
import pytest
from models import (
    ResultadoAnaliseFoto,
    ResultadoAnaliseIA,
)


def resultado_texto_valido():
    return ResultadoAnaliseIA(
        entrada_valida=True,
        motivo_invalidacao=None,
        tipo_pele="oleosa",
        sensivel=None,
        tem_espinha=True,
    )


def resultado_foto_valido():
    return ResultadoAnaliseFoto(
        imagem_adequada=True,
        tipo_pele="oleosa",
        confianca_tipo_pele="media",
        tem_espinha=True,
        marcas_pos_acne=False,
        vermelhidao=None,
        descamacao=False,
        brilho_excessivo=True,
        motivo_inadequacao=None,
    )


def test_gemini_preserva_o_contrato_existente(
    monkeypatch,
):
    argumentos = {}

    class InteracoesFalsas:
        def create(self, **kwargs):
            argumentos.update(kwargs)
            return SimpleNamespace(
                output_text=(
                    resultado_texto_valido()
                    .model_dump_json()
                )
            )

    cliente = SimpleNamespace(
        interactions=InteracoesFalsas()
    )

    monkeypatch.setenv(
        "AI_PROVIDER",
        "gemini",
    )
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "chave-de-teste",
    )
    monkeypatch.setattr(
        ai_providers,
        "_criar_cliente_gemini",
        lambda _chave: cliente,
    )

    resultado = (
        ai_providers
        .executar_analise_estruturada(
            "prompt de teste",
            ResultadoAnaliseIA,
            operacao="text",
        )
    )

    assert resultado.tipo_pele == "oleosa"
    assert argumentos["store"] is False
    assert argumentos[
        "response_format"
    ]["schema"] == (
        ResultadoAnaliseIA
        .model_json_schema()
    )


def test_openai_reutiliza_o_contrato_pydantic(
    monkeypatch,
):
    argumentos = {}

    class RespostasFalsas:
        def parse(self, **kwargs):
            argumentos.update(kwargs)
            return SimpleNamespace(
                output_parsed=(
                    resultado_texto_valido()
                )
            )

    cliente = SimpleNamespace(
        responses=RespostasFalsas()
    )

    monkeypatch.setenv(
        "AI_PROVIDER",
        "openai",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "chave-de-teste",
    )
    monkeypatch.setattr(
        ai_providers,
        "_criar_cliente_openai",
        lambda _chave: cliente,
    )

    resultado = (
        ai_providers
        .executar_analise_estruturada(
            "prompt de teste",
            ResultadoAnaliseIA,
            operacao="text",
        )
    )

    assert resultado.tipo_pele == "oleosa"
    assert argumentos["store"] is False
    assert (
        argumentos["text_format"]
        is ResultadoAnaliseIA
    )


def test_openai_envia_imagem_como_data_url(
    monkeypatch,
):
    argumentos = {}

    class RespostasFalsas:
        def parse(self, **kwargs):
            argumentos.update(kwargs)
            return SimpleNamespace(
                output_parsed=(
                    resultado_foto_valido()
                )
            )

    cliente = SimpleNamespace(
        responses=RespostasFalsas()
    )

    monkeypatch.setenv(
        "AI_PROVIDER",
        "openai",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "chave-de-teste",
    )
    monkeypatch.setattr(
        ai_providers,
        "_criar_cliente_openai",
        lambda _chave: cliente,
    )

    ai_providers.executar_analise_estruturada(
        "prompt de foto",
        ResultadoAnaliseFoto,
        operacao="photo",
        conteudo_imagem=b"imagem",
        mime_type="image/jpeg",
    )

    conteudo = (
        argumentos["input"]
        [0]["content"]
    )

    assert conteudo[1][
        "image_url"
    ].startswith(
        "data:image/jpeg;base64,"
    )


def test_anthropic_reutiliza_o_contrato_pydantic(
    monkeypatch,
):
    argumentos = {}

    class MensagensFalsas:
        def parse(self, **kwargs):
            argumentos.update(kwargs)
            return SimpleNamespace(
                parsed_output=(
                    resultado_texto_valido()
                )
            )

    cliente = SimpleNamespace(
        messages=MensagensFalsas()
    )

    monkeypatch.setenv(
        "AI_PROVIDER",
        "anthropic",
    )
    monkeypatch.setenv(
        "ANTHROPIC_API_KEY",
        "chave-de-teste",
    )
    monkeypatch.setattr(
        ai_providers,
        "_criar_cliente_anthropic",
        lambda _chave: cliente,
    )

    resultado = (
        ai_providers
        .executar_analise_estruturada(
            "prompt de teste",
            ResultadoAnaliseIA,
            operacao="text",
        )
    )

    assert resultado.tem_espinha is True
    assert (
        argumentos["output_format"]
        is ResultadoAnaliseIA
    )


def test_anthropic_envia_imagem_em_base64(
    monkeypatch,
):
    argumentos = {}

    class MensagensFalsas:
        def parse(self, **kwargs):
            argumentos.update(kwargs)
            return SimpleNamespace(
                parsed_output=(
                    resultado_foto_valido()
                )
            )

    cliente = SimpleNamespace(
        messages=MensagensFalsas()
    )

    monkeypatch.setenv(
        "AI_PROVIDER",
        "claude",
    )
    monkeypatch.setenv(
        "ANTHROPIC_API_KEY",
        "chave-de-teste",
    )
    monkeypatch.setattr(
        ai_providers,
        "_criar_cliente_anthropic",
        lambda _chave: cliente,
    )

    ai_providers.executar_analise_estruturada(
        "prompt de foto",
        ResultadoAnaliseFoto,
        operacao="photo",
        conteudo_imagem=b"imagem",
        mime_type="image/webp",
    )

    bloco_imagem = (
        argumentos["messages"]
        [0]["content"][0]
    )

    assert bloco_imagem["type"] == "image"
    assert bloco_imagem[
        "source"
    ]["media_type"] == "image/webp"


def test_limite_do_provedor_vira_erro_publico(
    monkeypatch,
):
    class ErroLimite(Exception):
        status_code = 429

    class RespostasFalsas:
        def parse(self, **_kwargs):
            raise ErroLimite()

    cliente = SimpleNamespace(
        responses=RespostasFalsas()
    )

    monkeypatch.setenv(
        "AI_PROVIDER",
        "openai",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "chave-de-teste",
    )
    monkeypatch.setattr(
        ai_providers,
        "_criar_cliente_openai",
        lambda _chave: cliente,
    )

    with pytest.raises(
        ai_providers.LimiteIAExcedido
    ):
        ai_providers.executar_analise_estruturada(
            "prompt de teste",
            ResultadoAnaliseIA,
            operacao="text",
        )


def test_saida_estruturada_invalida_eh_rejeitada(
    monkeypatch,
):
    class MensagensFalsas:
        def parse(self, **_kwargs):
            return SimpleNamespace(
                parsed_output=None
            )

    cliente = SimpleNamespace(
        messages=MensagensFalsas()
    )

    monkeypatch.setenv(
        "AI_PROVIDER",
        "anthropic",
    )
    monkeypatch.setenv(
        "ANTHROPIC_API_KEY",
        "chave-de-teste",
    )
    monkeypatch.setattr(
        ai_providers,
        "_criar_cliente_anthropic",
        lambda _chave: cliente,
    )

    with pytest.raises(
        ai_providers.RespostaIAInvalida
    ):
        ai_providers.executar_analise_estruturada(
            "prompt de teste",
            ResultadoAnaliseIA,
            operacao="text",
        )
