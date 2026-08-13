import pytest

import ai_service


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
