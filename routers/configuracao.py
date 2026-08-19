from fastapi import APIRouter, Depends, HTTPException

from admin_security import (
    bloquear_escrita_administrativa_em_producao,
)
from desktop_settings_service import (
    obter_configuracao_ia,
    salvar_configuracao_ia,
)
from models import (
    ConfiguracaoIAEntrada,
    ConfiguracaoIAResposta,
)


router = APIRouter(
    prefix="/admin/configuracao",
    tags=["Configuração local"],
    dependencies=[
        Depends(
            bloquear_escrita_administrativa_em_producao
        )
    ],
)


@router.get(
    "/ia",
    response_model=ConfiguracaoIAResposta,
)
def consultar_configuracao_ia():
    return obter_configuracao_ia()


@router.put(
    "/ia",
    response_model=ConfiguracaoIAResposta,
)
def atualizar_configuracao_ia(
    dados: ConfiguracaoIAEntrada,
):
    try:
        return salvar_configuracao_ia(dados)
    except RuntimeError as erro:
        raise HTTPException(
            status_code=409,
            detail=str(erro),
        ) from erro
