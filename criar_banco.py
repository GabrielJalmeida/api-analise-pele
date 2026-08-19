from database import conectar_banco


def criar_tabelas(
    *,
    silencioso: bool = False,
):
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
                DEFAULT '',

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
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            cliente_token_hash TEXT NOT NULL,
            cliente_nome TEXT NOT NULL,
            cliente_email TEXT NOT NULL,
            total REAL NOT NULL
                CHECK(total >= 0),
            status TEXT NOT NULL
                DEFAULT 'registrado'
                CHECK(status IN (
                    'registrado',
                    'cancelado'
                )),
            criado_em TEXT NOT NULL,
            expira_em TEXT NOT NULL,
            consentimento_retencao INTEGER NOT NULL
                CHECK(consentimento_retencao IN (0, 1))
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER,
            nome_produto TEXT NOT NULL,
            marca TEXT NOT NULL DEFAULT '',
            imagem_url TEXT NOT NULL DEFAULT '',
            preco_unitario REAL NOT NULL
                CHECK(preco_unitario >= 0),
            quantidade INTEGER NOT NULL
                CHECK(quantidade > 0),
            subtotal REAL NOT NULL
                CHECK(subtotal >= 0),
            FOREIGN KEY (pedido_id)
                REFERENCES pedidos(id)
                ON DELETE CASCADE
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
        idx_pedidos_cliente_criado
        ON pedidos (
            cliente_token_hash,
            criado_em DESC
        );
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_pedidos_expiracao
        ON pedidos (expira_em);
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

        if not silencioso:
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
