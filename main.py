from fastapi import FastAPI, HTTPException, UploadFile, Request
from fastapi.responses import JSONResponse
from typing import Literal
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import sqlite3

from services import produto_para_dict, buscar_produtos_compativeis, gerar_recomendacoes, obter_mensagem_inadequacao
from models import PerfilPele, NovoProduto, AtualizarProduto, TextoAnalisePele
from database import conectar_banco
from ai_service import interpretar_perfil, interpretar_foto, LimiteIAExcedido, ServicoIAIndisponivel, RespostaIAInvalida, ConfiguracaoIAInvalida

app = FastAPI()

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

#=========================================
# GERAL                                  #
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
# ANÁLISE DE PELE                        #
#=========================================

@app.post("/perfil-pele", tags=["Análise de Pele"])
def analisar_perfil_pele(perfil: PerfilPele):
    return perfil

@app.post("/analise-texto", tags=["Análise de Pele"])
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



@app.post("/analise-foto", tags=["Análise de Pele"])
async def analisar_foto(arquivo: UploadFile):

    if arquivo.content_type not in TIPOS_IMAGEM_PERMITIDOS:
        raise HTTPException(
            status_code=415,
            detail="Formato de imagem não permitido. Envie uma imagem JPG, PNG ou WEBP."
        )

    conteudo = await arquivo.read()

    if len(conteudo) > TAMANHO_MAXIMO_IMAGEM:
        raise HTTPException(
            status_code=413,
            detail="A imagem não pode ultrapassar 5 MB."
        )

    try:
        with Image.open(BytesIO(conteudo)) as imagem:
            formato_real = imagem.format
            imagem.verify()

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

    resultado = interpretar_foto(
        conteudo,
        mime_type_real
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
# RECOMENDAÇÕES                          #
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
