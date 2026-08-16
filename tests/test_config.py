from config import obter_origens_cors


def test_cors_usa_origem_padrao(
    monkeypatch,
):
    monkeypatch.delenv(
        "CORS_ORIGINS",
        raising=False,
    )

    origens = obter_origens_cors()

    assert origens == [
        "http://localhost:5173",
    ]


def test_cors_aceita_multiplas_origens(
    monkeypatch,
):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        (
            "http://localhost:5173,"
            "http://localhost:5174,"
            "https://exemplo.com"
        ),
    )

    origens = obter_origens_cors()

    assert origens == [
        "http://localhost:5173",
        "http://localhost:5174",
        "https://exemplo.com",
    ]