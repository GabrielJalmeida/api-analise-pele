from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from routers.analise import router as router_analise
from routers.geral import router as router_geral
from routers.produtos import router as router_produtos
from routers.recomendacoes import router as router_recomendacoes

from ai_service import LimiteIAExcedido, ServicoIAIndisponivel, RespostaIAInvalida, ConfiguracaoIAInvalida
from config import obter_origens_cors

app = FastAPI()

app.include_router(router_geral)
app.include_router(router_produtos)
app.include_router(router_recomendacoes)
app.include_router(router_analise)

app.add_middleware(
    CORSMiddleware,
    allow_origins=obter_origens_cors(),
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
        "bool_parsing": "Informe verdadeiro ou falso.",
        "int_parsing": "Informe um número inteiro válido.",
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
