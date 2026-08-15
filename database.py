import sqlite3
from pathlib import Path
from contextlib import contextmanager

CAMINHO_BANCO = Path(__file__).resolve().parent / "produtos.db"

def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    return conexao, cursor

@contextmanager
def gerenciar_banco():
    conexao, cursor = conectar_banco()

    try:
        yield conexao, cursor

    finally:
        conexao.close()

@contextmanager
def gerenciar_transacao():
    conexao, cursor = conectar_banco()

    try:
        yield conexao, cursor
        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()
        