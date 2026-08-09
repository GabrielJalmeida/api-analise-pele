from fastapi import FastAPI, HTTPException
from typing import Literal
import sqlite3

from services import produto_para_dict, buscar_produtos_compativeis, gerar_recomendacoes
from models import PerfilPele, NovoProduto, AtualizarProduto, TextoAnalisePele
from database import conectar_banco

app = FastAPI()

#=========================================
# GERAL
#=========================================

@app.get("/", tags=["Geral"])
def esta_funcionando():
    return {"message": "A API está funcionando!"}

status = "Em desenvolvimento"
projeto = "Análise de Pele para Loja de cosméticos"

@app.get("/status", tags=["Geral"])
def obter_status():
    return {"status": status, "projeto": projeto}

#=========================================
# ANÁLISE DE PELE
#=========================================

@app.post("/perfil-pele", tags=["Análise de Pele"])
def analisar_perfil_pele(perfil: PerfilPele):
    return perfil

@app.post("/analise-texto", tags=["Análise de Pele"])
def analisar_texto(dados: TextoAnalisePele):
    return {
        "texto_recebido": dados.texto
    }

#=========================================
# PRODUTOS
#=========================================

@app.get("/produto/{id_produto}", tags=["Produtos"])
def obter_produto(id_produto: int):
    conexao, cursor = conectar_banco()

    cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_produto,))
    produto = cursor.fetchone()
    conexao.close()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
            )
    dados_produtos = produto_para_dict(produto)

    return dados_produtos

@app.get("/produtos", tags=["Produtos"])
def listar_produtos():
    conexao, cursor = conectar_banco()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conexao.close()

    lista_produtos = []
    for produto in produtos:
        dados_produto = produto_para_dict(produto)
        lista_produtos.append(dados_produto)

    return lista_produtos


@app.post("/produto", tags=["Produtos"])
def criar_produto(novo_produto: NovoProduto):
    conexao, cursor = conectar_banco()

    try:
        cursor.execute(
        """
    INSERT INTO produtos (nome, preco, estoque, tipo_pele, pele_sensivel, indicado_para_espinha, ativo, categoria)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""",
    (novo_produto.nome, novo_produto.preco, novo_produto.estoque, novo_produto.tipo_pele, novo_produto.pele_sensivel, novo_produto.indicado_para_espinha, novo_produto.ativo, novo_produto.categoria)
    )
            
        id_produto = cursor.lastrowid

        conexao.commit()
        conexao.close()


    except sqlite3.IntegrityError:
        conexao.close()
        raise HTTPException(
            status_code=409,
            detail="Produto já cadastrado"
        )

    
    return {
        "id": id_produto,
        "nome": novo_produto.nome,
        "preco": novo_produto.preco,
        "estoque": novo_produto.estoque,
        "tipo_pele": novo_produto.tipo_pele,
        "pele_sensivel": novo_produto.pele_sensivel,
        "indicado_para_espinha": novo_produto.indicado_para_espinha,
        "ativo": novo_produto.ativo,
        "categoria": novo_produto.categoria
        }


@app.patch("/produto/{id_produto}", tags=["Produtos"])
def atualizar_produto(id_produto: int, dados: AtualizarProduto):
    conexao, cursor = conectar_banco()

    cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_produto,))

    produto = cursor.fetchone()

    if not produto:
        conexao.close()
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )
    
    dados_atualizados = dados.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not dados_atualizados:
        conexao.close()
        raise HTTPException(
            status_code=400,
            detail="Nenhum dado enviado para atualização"
        )

    campos_sql = []
    valores_sql = []

    for campo, valor in dados_atualizados.items():
        campos_sql.append(f"{campo} = ?")
        valores_sql.append(valor)

    campos_formatados = ", ".join(campos_sql)

    sql = f"""
    UPDATE produtos
    SET {campos_formatados}
    WHERE id = ?
    """

    valores_sql.append(id_produto)

    try:
        cursor.execute(sql, valores_sql)
        conexao.commit()

    except sqlite3.IntegrityError:
        conexao.close()
        raise HTTPException(
            status_code=409,
            detail="Produto já cadastrado"
        )

    cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_produto,))
    produto_atualizado = cursor.fetchone()
    conexao.close()

    produto_atualizado = produto_para_dict(produto_atualizado)

    return produto_atualizado

#=========================================
# RECOMENDAÇÕES
#=========================================

@app.get("/recomendacoes/{tipo_pele}", tags=["Recomendações"])
def recomendar_produtos(tipo_pele: Literal["oleosa", "seca", "mista", "normal"]):

    recomendacoes = buscar_produtos_compativeis(tipo_pele)

    lista_recomendacoes = []

    for recomendacao in recomendacoes:
        recomendacoes_atualizadas = produto_para_dict(recomendacao)

        lista_recomendacoes.append(recomendacoes_atualizadas)

    return lista_recomendacoes

@app.post("/recomendacoes", tags=["Recomendações"])
def recomendar_por_perfil(perfil: PerfilPele):

    return gerar_recomendacoes(perfil)
