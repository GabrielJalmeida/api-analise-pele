from database import conectar_banco


def criar_tabelas():
    conexao, cursor = conectar_banco()

    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nome TEXT NOT NULL UNIQUE,

            preco REAL NOT NULL
                CHECK(preco > 0),

            estoque INTEGER NOT NULL
                CHECK(estoque >= 0),

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
                CHECK(ativo IN (0, 1)),

            marca TEXT NOT NULL
                DEFAULT 'Lumina Skin',

            descricao_curta TEXT NOT NULL
                DEFAULT '',

            imagem_url TEXT NOT NULL
                DEFAULT '',

            conteudo TEXT NOT NULL
                DEFAULT '',

            ativos_principais TEXT NOT NULL
                DEFAULT ''
        );
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_produtos_ativo_categoria
        ON produtos (
            ativo,
            categoria
        );
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_produtos_ativo_tipo_pele
        ON produtos (
            ativo,
            tipo_pele
        );
        """)

        conexao.commit()

        print(
            "Banco de dados criado "
            "com sucesso."
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


if __name__ == "__main__":
    criar_tabelas()