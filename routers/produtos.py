import sqlite3
from typing import Literal

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from database import gerenciar_banco, gerenciar_transacao
from models import (
    AtualizarProduto,
    NovoProduto,
    ProdutoResposta,
    RespostaProdutoDesativado,
    RespostaUploadImagemProduto,
)
from services import produto_para_dict
from product_image_service import (
    ImagemProdutoInvalida,
    TAMANHO_MAXIMO_BYTES,
    salvar_imagem_produto,
)


router = APIRouter(tags=["Produtos"])

@router.post(
    "/produtos/imagem",
    response_model=RespostaUploadImagemProduto,
    status_code=201,
)
async def enviar_imagem_produto(
    arquivo: UploadFile = File(...),
    nome_produto: str = Form(...),
    categoria: Literal[
        "limpeza",
        "hidratante",
        "serum",
        "protetor_solar",
        "outros",
    ] = Form(...),
):
    nome_produto = nome_produto.strip()

    if len(nome_produto) < 2:
        raise HTTPException(
            status_code=400,
            detail=(
                "O nome do produto deve conter "
                "pelo menos 2 caracteres"
            ),
        )

    if len(nome_produto) > 100:
        raise HTTPException(
            status_code=400,
            detail=(
                "O nome do produto não pode "
                "ultrapassar 100 caracteres"
            ),
        )

    try:
        conteudo = await arquivo.read(
            TAMANHO_MAXIMO_BYTES + 1
        )

        imagem_url = salvar_imagem_produto(
            conteudo=conteudo,
            nome_produto=nome_produto,
            categoria=categoria,
        )

    except ImagemProdutoInvalida as erro:
        raise HTTPException(
            status_code=400,
            detail=str(erro),
        ) from erro

    finally:
        await arquivo.close()

    return {
        "status": "imagem_salva",
        "imagem_url": imagem_url,
    }

@router.get(
    "/produto/{id_produto}",
    response_model=ProdutoResposta,
)
def obter_produto(id_produto: int):
    with gerenciar_banco() as (conexao, cursor):
        cursor.execute(
            "SELECT * FROM produtos WHERE id = ?",
            (id_produto,),
        )

        produto = cursor.fetchone()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        )

    return produto_para_dict(produto)


@router.get(
    "/produtos",
    response_model=list[ProdutoResposta],
)
def listar_produtos(
    busca: str | None = None,
    categoria: Literal[
        "limpeza",
        "hidratante",
        "serum",
        "protetor_solar",
        "outros",
    ]
    | None = None,
    tipo_pele: Literal[
        "oleosa",
        "seca",
        "mista",
        "normal",
        "todos",
    ]
    | None = None,
    ativo: bool | None = None,
):
    sql = "SELECT * FROM produtos"
    condicoes = []
    valores = []

    if busca:
        busca = busca.strip()

        if busca:
            condicoes.append("nome LIKE ?")
            valores.append(f"%{busca}%")

    if categoria is not None:
        condicoes.append("categoria = ?")
        valores.append(categoria)

    if tipo_pele is not None:
        condicoes.append("tipo_pele = ?")
        valores.append(tipo_pele)

    if ativo is not None:
        condicoes.append("ativo = ?")
        valores.append(ativo)

    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)

    with gerenciar_banco() as (conexao, cursor):
        cursor.execute(sql, valores)
        produtos = cursor.fetchall()

    return [
        produto_para_dict(produto)
        for produto in produtos
    ]


@router.post(
    "/produto",
    response_model=ProdutoResposta,
)
def criar_produto(novo_produto: NovoProduto):
    try:
        with gerenciar_transacao() as (conexao, cursor):
            cursor.execute(
                """
                INSERT INTO produtos (
                    nome,
                    preco,
                    estoque,
                    tipo_pele,
                    pele_sensivel,
                    indicado_para_espinha,
                    ativo,
                    categoria,
                    marca,
                    descricao_curta,
                    imagem_url,
                    conteudo,
                    ativos_principais
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    novo_produto.nome,
                    novo_produto.preco,
                    novo_produto.estoque,
                    novo_produto.tipo_pele,
                    novo_produto.pele_sensivel,
                    novo_produto.indicado_para_espinha,
                    novo_produto.ativo,
                    novo_produto.categoria,
                    novo_produto.marca,
                    novo_produto.descricao_curta,
                    novo_produto.imagem_url,
                    novo_produto.conteudo,
                    novo_produto.ativos_principais,
                ),
            )

            id_produto = cursor.lastrowid

    except sqlite3.IntegrityError as erro:
        if (
            erro.sqlite_errorcode
            == sqlite3.SQLITE_CONSTRAINT_UNIQUE
        ):
            raise HTTPException(
                status_code=409,
                detail="Produto já cadastrado",
            )

        raise HTTPException(
            status_code=400,
            detail=(
                "Os dados do produto violam "
                "uma regra do banco de dados"
            ),
        )

    return {
        "id": id_produto,
        "nome": novo_produto.nome,
        "preco": novo_produto.preco,
        "estoque": novo_produto.estoque,
        "tipo_pele": novo_produto.tipo_pele,
        "pele_sensivel": novo_produto.pele_sensivel,
        "indicado_para_espinha": (
            novo_produto.indicado_para_espinha
        ),
        "ativo": novo_produto.ativo,
        "categoria": novo_produto.categoria,
        "marca": novo_produto.marca,
        "descricao_curta": novo_produto.descricao_curta,
        "imagem_url": novo_produto.imagem_url,
        "conteudo": novo_produto.conteudo,
        "ativos_principais": novo_produto.ativos_principais,
    }

@router.patch(
    "/produto/{id_produto}",
    response_model=ProdutoResposta,
)
def atualizar_produto(
    id_produto: int,
    dados: AtualizarProduto,
):
    dados_atualizados = dados.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    if not dados_atualizados:
        raise HTTPException(
            status_code=400,
            detail="Nenhum dado enviado para atualização",
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
        with gerenciar_transacao() as (conexao, cursor):
            cursor.execute(
                "SELECT * FROM produtos WHERE id = ?",
                (id_produto,),
            )

            produto = cursor.fetchone()

            if not produto:
                raise HTTPException(
                    status_code=404,
                    detail="Produto não encontrado",
                )

            cursor.execute(sql, valores_sql)

            cursor.execute(
                "SELECT * FROM produtos WHERE id = ?",
                (id_produto,),
            )

            produto_atualizado = cursor.fetchone()

    except sqlite3.IntegrityError as erro:
        if (
            erro.sqlite_errorcode
            == sqlite3.SQLITE_CONSTRAINT_UNIQUE
        ):
            raise HTTPException(
                status_code=409,
                detail="Produto já cadastrado",
            )

        raise HTTPException(
            status_code=400,
            detail=(
                "Os dados do produto violam "
                "uma regra do banco de dados"
            ),
        )

    return produto_para_dict(produto_atualizado)


@router.delete(
    "/produto/{id_produto}",
    response_model=RespostaProdutoDesativado,
)
def desativar_produto(id_produto: int):
    with gerenciar_transacao() as (conexao, cursor):
        cursor.execute(
            "SELECT * FROM produtos WHERE id = ?",
            (id_produto,),
        )

        produto = cursor.fetchone()

        if not produto:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado",
            )

        if not produto["ativo"]:
            raise HTTPException(
                status_code=409,
                detail="O produto já está inativo",
            )

        cursor.execute(
            """
            UPDATE produtos
            SET ativo = 0
            WHERE id = ?
            """,
            (id_produto,),
        )

    return {
        "status": "produto_desativado",
        "mensagem": "Produto desativado com sucesso",
        "id": id_produto,
    }