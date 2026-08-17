import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

RAIZ_PROJETO = Path(__file__).resolve().parents[1]

if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

import database
from criar_banco import criar_tabelas
from main import app


@pytest.fixture
def banco_temporario(tmp_path, monkeypatch):
    caminho_banco = tmp_path / "produtos_teste.db"
    monkeypatch.setattr(database, "CAMINHO_BANCO", caminho_banco)
    criar_tabelas()
    return caminho_banco


@pytest.fixture
def client(banco_temporario):
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def produto_valido():
    return {
        "nome": "Gel de limpeza teste",

        "marca": "Lumina Skin",
        "descricao_curta": (
            "Gel de limpeza facial de textura leve "
            "para a rotina diária de cuidados."
        ),
        "imagem_url": (
            "/media/produtos/"
            "gel-limpeza-teste.webp"
        ),
        "conteudo": "150 ml",
        "ativos_principais": (
            "Niacinamida e pantenol"
        ),

        "preco": 39.90,
        "estoque": 10,
        "categoria": "limpeza",
        "tipo_pele": "oleosa",
        "pele_sensivel": True,
        "indicado_para_espinha": True,
        "ativo": True,
    }