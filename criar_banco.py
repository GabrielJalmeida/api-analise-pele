from database import conectar_banco

def criar_tabelas():
    conexao, cursor = conectar_banco()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        preco REAL NOT NULL CHECK(preco > 0),
        estoque INTEGER NOT NULL CHECK(estoque >= 0),

        categoria TEXT NOT NULL
            CHECK(categoria IN (
                'limpeza',
                'hidratante',
                'serum',
                'protetor_solar',
                'outros'
            )),

        tipo_pele TEXT NOT NULL
            CHECK(tipo_pele IN (
                'oleosa',
                'seca',
                'mista',
                'normal',
                'todos'
            )),

        pele_sensivel INTEGER NOT NULL
            CHECK(pele_sensivel IN (0, 1)),

        indicado_para_espinha INTEGER NOT NULL
            CHECK(indicado_para_espinha IN (0, 1)),

        ativo INTEGER NOT NULL DEFAULT 1
            CHECK(ativo IN (0, 1))
    );
    """)

    conexao.commit()

    conexao.close()

if __name__ == "__main__":
    criar_tabelas()
