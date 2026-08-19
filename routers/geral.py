from fastapi import APIRouter

from config import VERSAO_APLICACAO


router = APIRouter(tags=["Geral"])

STATUS_PROJETO = "operacional"
NOME_PROJETO = "Análise de Pele para Loja de cosméticos"


@router.get("/")
def esta_funcionando():
    return {"message": "A API está funcionando!"}


@router.get("/status")
def obter_status():
    return {
        "status": STATUS_PROJETO,
        "projeto": NOME_PROJETO,
        "versao": VERSAO_APLICACAO,
    }
