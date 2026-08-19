import asyncio
import logging
from contextlib import asynccontextmanager
from contextlib import suppress
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers.analise import router as router_analise
from routers.geral import router as router_geral
from routers.produtos import router as router_produtos
from routers.recomendacoes import router as router_recomendacoes
from routers.importacao import router as router_importacao
from routers.pedidos import router as router_pedidos

from ai_service import LimiteIAExcedido, ServicoIAIndisponivel, RespostaIAInvalida, ConfiguracaoIAInvalida
from config import (
    VERSAO_APLICACAO,
    obter_diretorio_media,
    obter_origens_cors,
)
from criar_banco import criar_tabelas
from order_service import limpar_pedidos_expirados

MEDIA_DIR = obter_diretorio_media()
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
LOGGER = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    criar_tabelas(silencioso=True)
    limpar_pedidos_expirados()

    async def limpar_historico_periodicamente():
        while True:
            await asyncio.sleep(24 * 60 * 60)
            await asyncio.to_thread(
                limpar_pedidos_expirados
            )

    tarefa_limpeza = asyncio.create_task(
        limpar_historico_periodicamente()
    )

    try:
        yield
    finally:
        tarefa_limpeza.cancel()

        with suppress(asyncio.CancelledError):
            await tarefa_limpeza


app = FastAPI(
    title="API de Análise de Pele",
    version=VERSAO_APLICACAO,
    description=(
        "Análise cosmética assistida por IA, recomendações "
        "determinísticas e catálogo administrável."
    ),
    lifespan=ciclo_de_vida,
)

app.mount(
    "/media",
    StaticFiles(directory=MEDIA_DIR),
    name="media",
)

app.include_router(router_geral)
app.include_router(router_produtos)
app.include_router(router_recomendacoes)
app.include_router(router_analise)
app.include_router(router_importacao)
app.include_router(router_pedidos)

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
        "X-Cliente-Token",
    ],
    expose_headers=[
        "Server-Timing",
        "X-Request-ID",
        "X-Cliente-Token",
    ],
)


@app.middleware("http")
async def adicionar_observabilidade(
    request: Request,
    call_next,
):
    request_id = uuid4().hex
    inicio = perf_counter()

    try:
        resposta = await call_next(request)
    except Exception:
        duracao_ms = (
            perf_counter() - inicio
        ) * 1000

        LOGGER.exception(
            "request_failed request_id=%s "
            "method=%s path=%s duration_ms=%.1f",
            request_id,
            request.method,
            request.url.path,
            duracao_ms,
        )
        raise

    duracao_ms = (
        perf_counter() - inicio
    ) * 1000

    resposta.headers[
        "X-Request-ID"
    ] = request_id
    resposta.headers[
        "Server-Timing"
    ] = f"app;dur={duracao_ms:.1f}"

    if request.url.path in {
        "/analise-foto",
        "/analise-texto",
    }:
        LOGGER.info(
            "request_completed request_id=%s "
            "method=%s path=%s status=%s "
            "duration_ms=%.1f",
            request_id,
            request.method,
            request.url.path,
            resposta.status_code,
            duracao_ms,
        )

    return resposta

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
