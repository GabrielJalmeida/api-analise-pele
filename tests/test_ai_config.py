import pytest

import ai_service
from ai_providers import (
    obter_configuracao_provedor,
    obter_modelo_anthropic,
    obter_modelo_openai,
    obter_provedor_ia,
)


def test_modelo_padrao_eh_o_definido_para_o_projeto(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    assert ai_service.obter_modelo_gemini() == "gemini-3.5-flash-lite"


def test_modelo_pode_ser_alterado_por_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "modelo-de-teste")

    assert ai_service.obter_modelo_gemini() == "modelo-de-teste"


def test_cliente_so_exige_chave_quando_a_ia_eh_usada(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ai_service.ConfiguracaoIAInvalida):
        ai_service.obter_cliente()


def test_gemini_eh_o_provedor_padrao(
    monkeypatch,
):
    monkeypatch.delenv(
        "AI_PROVIDER",
        raising=False,
    )

    assert obter_provedor_ia() == "gemini"


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("google", "gemini"),
        ("claude", "anthropic"),
        ("openai", "openai"),
    ],
)
def test_provedor_aceita_nomes_documentados(
    monkeypatch,
    valor,
    esperado,
):
    monkeypatch.setenv(
        "AI_PROVIDER",
        valor,
    )

    assert obter_provedor_ia() == esperado


def test_provedor_invalido_eh_rejeitado(
    monkeypatch,
):
    monkeypatch.setenv(
        "AI_PROVIDER",
        "provedor-inexistente",
    )

    with pytest.raises(
        ai_service.ConfiguracaoIAInvalida
    ):
        obter_provedor_ia()


def test_openai_exige_apenas_a_propria_chave(
    monkeypatch,
):
    monkeypatch.setenv(
        "AI_PROVIDER",
        "openai",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "chave-de-teste",
    )
    monkeypatch.delenv(
        "GEMINI_API_KEY",
        raising=False,
    )

    configuracao = (
        obter_configuracao_provedor()
    )

    assert configuracao.nome == "openai"
    assert (
        configuracao.modelo
        == obter_modelo_openai()
    )


def test_modelos_alternativos_podem_ser_configurados(
    monkeypatch,
):
    monkeypatch.setenv(
        "OPENAI_MODEL",
        "modelo-openai-teste",
    )
    monkeypatch.setenv(
        "ANTHROPIC_MODEL",
        "modelo-anthropic-teste",
    )

    assert (
        obter_modelo_openai()
        == "modelo-openai-teste"
    )
    assert (
        obter_modelo_anthropic()
        == "modelo-anthropic-teste"
    )
