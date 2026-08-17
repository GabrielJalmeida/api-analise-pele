import sqlite3
from contextlib import contextmanager

from config import obter_caminho_banco


CAMINHO_BANCO = obter_caminho_banco()

def conectar_banco():
    CAMINHO_BANCO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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
        