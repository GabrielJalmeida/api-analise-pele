from fastapi import FastAPI, HTTPException, UploadFile, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from typing import Literal
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import sqlite3

from routers.geral import router as router_geral

from services import produto_para_dict, gerar_recomendacoes, obter_mensagem_inadequacao
from models import PerfilPele, NovoProduto, AtualizarProduto, TextoAnalisePele, ProdutoResposta, RespostaRecomendacoes, RespostaAnaliseTextoInsuficiente, RespostaAnaliseFotoInadequada, RespostaAnaliseFotoInsuficiente, RespostaAnaliseFotoSucesso, RespostaProdutoDesativado
from database import gerenciar_banco, gerenciar_transacao
from ai_service import interpretar_perfil, interpretar_foto, LimiteIAExcedido, ServicoIAIndisponivel, RespostaIAInvalida, ConfiguracaoIAInvalida

app = FastAPI()

app.include_router(router_geral)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "DELETE",
    ],
    allow_headers=[
        "Content-Type",
    ],
)

MIME_POR_FORMATO = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp"
}

FORMATOS_IMAGEM_PERMITIDOS = {
    "JPEG",
    "PNG",
    "WEBP"
}

TIPOS_IMAGEM_PERMITIDOS = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

TAMANHO_MAXIMO_IMAGEM = 5 * 1024 * 1024
TOTAL_MAXIMO_PIXELS = 20_000_000

# ========================================
# TRATAMENTO GLOBAL DE ERROS             #
# ========================================

@app.exception_handler(LimiteIAExcedido)
async def tratar_limite_ia(
    request: Request,
    erro: LimiteIAExcedido
):
    return JSONResponse(
        status_code=503,
        content={
            "status": "limite_ia_excedido",
            "mensagem": "O serviço de análise atingiu o limite temporário de uso. Tente novamente mais tarde."
        }
    )


@app.exception_handler(ServicoIAIndisponivel)
async def tratar_servico_ia_indisponivel(
    request: Request,
    erro: ServicoIAIndisponivel
):
    return JSONResponse(
        status_code=503,
        content={
            "status": "servico_ia_indisponivel",
            "mensagem": "O serviço de análise está temporariamente indisponível. Tente novamente em alguns instantes."
        }
    )


@app.exception_handler(RespostaIAInvalida)
async def tratar_resposta_ia_invalida(
    request: Request,
    erro: RespostaIAInvalida
):
    return JSONResponse(
        status_code=502,
        content={
            "status": "resposta_ia_invalida",
            "mensagem": "Não foi possível concluir a análise. Tente novamente."
        }
    )


@app.exception_handler(ConfiguracaoIAInvalida)
async def tratar_configuracao_ia_invalida(
    request: Request,
    erro: ConfiguracaoIAInvalida
):
    return JSONResponse(
        status_code=503,
        content={
            "status": "servico_ia_indisponivel",
            "mensagem": "O serviço de análise está temporariamente indisponível."
        }
    )


@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(
    request: Request,
    erro: RequestValidationError
):
    
    mensagens_por_tipo = {
        "missing": "Campo obrigatório.",
        "literal_error": "Valor inválido.",
        "extra_forbidden": "Campo não permitido.",
        "bool_parsing": "Informe um número inteiro válido.",
        "float_parsing": "Informe um número válido.",
        "string_type": "Informe um texto válido.",
    }

    erros_formatados = []

    for detalhe in erro.errors():
        localizacao = detalhe["loc"]

        campo = ".".join(
            str(parte)
            for parte in localizacao
            if parte not in {"body", "query", "path"}
        )

        mensagem = mensagens_por_tipo.get(
            detalhe["type"],
            detalhe["msg"]
        )

        erros_formatados.append(
            {
                "campo": campo,
                "mensagem": mensagem
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "status": "dados_invalidos",
            "mensagem": "Os dados enviados são inválidos.",
            "erros": erros_formatados
        }
    )


#=========================================
# ANÁLISE DE PELE                        #
#=========================================

@app.post(
        "/analise-texto",
         response_model=RespostaRecomendacoes | RespostaAnaliseTextoInsuficiente,
        tags=["Análise de Pele"])
def analisar_texto(dados: TextoAnalisePele):
    resultado = interpretar_perfil(dados.texto)

    if resultado.tipo_pele is None:
        return {
            "status": "informacoes_insuficientes",
            "mensagem": "Não foi possível identificar o tipo de pele com as informações fornecidas.",
            "perfil": resultado,
            "total_recomendacoes": 0,
            "recomendacoes": {}
        }

    perfil = PerfilPele(
        tipo_pele=resultado.tipo_pele,
        sensivel=resultado.sensivel,
        tem_espinha=resultado.tem_espinha
    )

    return gerar_recomendacoes(perfil)



@app.post(
        "/analise-foto",
         response_model=(
             RespostaAnaliseFotoSucesso
             | RespostaAnaliseFotoInadequada
             | RespostaAnaliseFotoInsuficiente
         ),
         tags=["Análise de Pele"]
         )
async def analisar_foto(arquivo: UploadFile):

    if arquivo.content_type not in TIPOS_IMAGEM_PERMITIDOS:
        raise HTTPException(
            status_code=415,
            detail="Formato de imagem não permitido. Envie uma imagem JPG, PNG ou WEBP."
        )

    conteudo = await arquivo.read(TAMANHO_MAXIMO_IMAGEM + 1)

    if len(conteudo) > TAMANHO_MAXIMO_IMAGEM:
        raise HTTPException(
            status_code=413,
            detail="A imagem não pode ultrapassar 5 MB."
        )

    try:
        with Image.open(BytesIO(conteudo)) as imagem:
            formato_real = imagem.format
            largura, altura = imagem.size

            if largura * altura > TOTAL_MAXIMO_PIXELS:
                raise HTTPException(
                    status_code=413,
                    detail="A imagem não pode ultrapassar 20 megapixels."
                )

            imagem.verify()

    except HTTPException:
        raise

    except Image.DecompressionBombError:
        raise HTTPException(
            status_code=413,
            detail="As dimensões da imagem são grandes demais."
        )

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=415,
            detail="O arquivo enviado não é uma imagem válida."
        )

    if formato_real not in FORMATOS_IMAGEM_PERMITIDOS:
        raise HTTPException(
            status_code=415,
            detail="Formato de imagem não permitido. Envie uma imagem JPG, PNG ou WEBP."
        )

    mime_type_real = MIME_POR_FORMATO[formato_real]

    resultado = await run_in_threadpool(
        interpretar_foto,
        conteudo,
        mime_type_real,
    )

    if not resultado.imagem_adequada:
        return {
            "status": "imagem_inadequada",
            "mensagem": obter_mensagem_inadequacao(
                resultado.motivo_inadequacao
            ),
            "analise": resultado.model_dump()
        }

    if resultado.tipo_pele is None:
        return {
            "status": "informacoes_insuficientes",
            "mensagem": "A imagem foi analisada, mas não foi possível estimar o tipo de pele com segurança.",
            "analise": resultado.model_dump(),
            "total_recomendacoes": 0,
            "recomendacoes": {}
        }

    perfil = PerfilPele(
        tipo_pele=resultado.tipo_pele,
        sensivel=None,
        tem_espinha=resultado.tem_espinha
    )

    recomendacoes = gerar_recomendacoes(perfil)

    return {
        "status": "sucesso",
        "analise": resultado.model_dump(),
        **recomendacoes
    }

#=========================================
# PRODUTOS                               #
#=========================================

@app.get(
        "/produto/{id_produto}",
         response_model=ProdutoResposta,
         tags=["Produtos"])
def obter_produto(id_produto: int):
    with gerenciar_banco() as (conexao, cursor):

        cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_produto,))
        produto = cursor.fetchone()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
            )
    dados_produtos = produto_para_dict(produto)

    return dados_produtos

@app.get(
        "/produtos",
        response_model=list[ProdutoResposta],
        tags=["Produtos"])
def listar_produtos(
    busca: str | None = None,
    categoria: Literal[
        "limpeza",
        "hidratante",
        "serum",
        "protetor_solar",
        "outros"
    ] | None = None,
    tipo_pele: Literal[
        "oleosa",
        "seca",
        "mista",
        "normal",
        "todos"
    ] | None = None,
    ativo: bool | None = None
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

    lista_produtos = []

    for produto in produtos:
        dados_produto = produto_para_dict(produto)
        lista_produtos.append(dados_produto)

    return lista_produtos


@app.post(
        "/produto",
        response_model=ProdutoResposta,
        tags=["Produtos"])
def criar_produto(novo_produto: NovoProduto):

    try:
        with gerenciar_transacao() as (conexao, cursor):
            cursor.execute(
        """
    INSERT INTO produtos (nome, preco, estoque, tipo_pele, pele_sensivel, indicado_para_espinha, ativo, categoria)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""",
    (novo_produto.nome, novo_produto.preco, novo_produto.estoque, novo_produto.tipo_pele, novo_produto.pele_sensivel, novo_produto.indicado_para_espinha, novo_produto.ativo, novo_produto.categoria)
    )
            
            id_produto = cursor.lastrowid


    except sqlite3.IntegrityError as erro:
        if erro.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
            raise HTTPException(
                status_code=409,
                detail="Produto já cadastrado"
            )

        raise HTTPException(
            status_code=400,
            detail="Os dados do produto violam uma regra do banco de dados"
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


@app.patch(
        "/produto/{id_produto}",
         response_model=ProdutoResposta,
        tags=["Produtos"])
def atualizar_produto(id_produto: int, dados: AtualizarProduto):

    dados_atualizados = dados.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not dados_atualizados:
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
        with gerenciar_transacao() as (conexao, cursor):

            cursor.execute(
                "SELECT * FROM produtos WHERE id = ?",
                (id_produto,)
            )

            produto = cursor.fetchone()

            if not produto:
                raise HTTPException(
                    status_code=404,
                    detail="Produto não encontrado"
                )

            cursor.execute(sql, valores_sql)

            cursor.execute(
                "SELECT * FROM produtos WHERE id = ?",
                (id_produto,)
            )

            produto_atualizado = cursor.fetchone()


    except sqlite3.IntegrityError as erro:
        if erro.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
            raise HTTPException(
                status_code=409,
                detail="Produto já cadastrado"
            )

        raise HTTPException(
            status_code=400,
            detail="Os dados do produto violam uma regra do banco de dados"
        )
    
    return produto_para_dict(produto_atualizado)

@app.delete(
        "/produto/{id_produto}",
         response_model=RespostaProdutoDesativado, tags=["Produtos"])
def desativar_produto(id_produto: int):

    with gerenciar_transacao() as (conexao, cursor):
        cursor.execute(
            "SELECT * FROM produtos WHERE id = ?",
            (id_produto,)
        )

        produto = cursor.fetchone()

        if not produto:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado"
            )

        if not produto["ativo"]:
            raise HTTPException(
                status_code=409,
                detail="O produto já está inativo"
            )

        cursor.execute(
            """
UPDATE produtos
SET ativo = 0
WHERE id = ?
""",
(id_produto,)
        )

    return {
        "status": "produto_desativado",
        "mensagem": "Produto desativado com sucesso",
        "id": id_produto
    }

#=========================================
# RECOMENDAÇÕES                          #
#=========================================

@app.post(
        "/recomendacoes",
         response_model=RespostaRecomendacoes, tags=["Recomendações"]
         )
def recomendar_por_perfil(perfil: PerfilPele):

    return gerar_recomendacoes(perfil)
