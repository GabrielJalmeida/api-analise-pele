import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).resolve().parent / "produtos.db"

def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    return conexao, cursor