from config import (
    ambiente_producao,
    obter_caminho_banco,
    obter_diretorio_media,
    obter_origens_cors,
)


def test_caminho_banco_pode_ser_configurado(
    monkeypatch,
    tmp_path,
):
    caminho_esperado = tmp_path / "catalogo.db"
    monkeypatch.setenv(
        "DATABASE_PATH",
        str(caminho_esperado),
    )

    assert obter_caminho_banco() == caminho_esperado


def test_desktop_isola_banco_e_midias_em_diretorio_de_dados(
    monkeypatch,
    tmp_path,
):
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("MEDIA_PATH", raising=False)
    monkeypatch.setenv("LUMINA_DATA_DIR", str(tmp_path))

    assert obter_caminho_banco() == (
        tmp_path / "data" / "produtos.db"
    )
    assert obter_diretorio_media() == (
        tmp_path / "media"
    )


def test_ambiente_producao_eh_configuravel(
    monkeypatch,
):
    monkeypatch.setenv("APP_ENV", "production")

    assert ambiente_producao() is True


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
        "http://localhost:5174",
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
