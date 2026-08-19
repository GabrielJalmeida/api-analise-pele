from fastapi import APIRouter, Depends, Header, HTTPException

from admin_security import (
    bloquear_escrita_administrativa_em_producao,
)
from models import (
    NovoPedido,
    PedidoResposta,
    RespostaCriacaoPedido,
    RespostaExclusaoHistorico,
    RespostaHistoricoPedidos,
)
from order_service import (
    PedidoInvalido,
    RETENCAO_DIAS,
    criar_pedido,
    excluir_historico,
    listar_historico,
    listar_pedidos_admin,
)


router = APIRouter(tags=["Pedidos demonstrativos"])


def _validar_token(token: str | None) -> str:
    if token is None:
        raise HTTPException(
            status_code=400,
            detail="Informe o identificador do histórico",
        )

    token = token.strip()

    if not 32 <= len(token) <= 128:
        raise HTTPException(
            status_code=400,
            detail="Identificador do histórico inválido",
        )

    return token


@router.post(
    "/pedidos",
    response_model=RespostaCriacaoPedido,
    status_code=201,
)
def registrar_pedido(dados: NovoPedido):
    try:
        pedido = criar_pedido(dados)
    except PedidoInvalido as erro:
        raise HTTPException(
            status_code=409,
            detail=str(erro),
        ) from erro

    return {
        "status": "pedido_registrado",
        "mensagem": (
            "Pedido demonstrativo registrado. "
            "Nenhuma cobrança foi realizada."
        ),
        "pedido": pedido,
    }


@router.get(
    "/pedidos/historico",
    response_model=RespostaHistoricoPedidos,
)
def obter_historico(
    x_cliente_token: str | None = Header(
        default=None,
        alias="X-Cliente-Token",
    ),
):
    token = _validar_token(x_cliente_token)
    pedidos = listar_historico(token)

    return {
        "retencao_dias": RETENCAO_DIAS,
        "total": len(pedidos),
        "pedidos": pedidos,
    }


@router.delete(
    "/pedidos/historico",
    response_model=RespostaExclusaoHistorico,
)
def apagar_historico(
    x_cliente_token: str | None = Header(
        default=None,
        alias="X-Cliente-Token",
    ),
):
    token = _validar_token(x_cliente_token)

    return {
        "status": "historico_excluido",
        "pedidos_removidos": excluir_historico(
            token
        ),
    }


@router.get(
    "/admin/pedidos",
    response_model=list[PedidoResposta],
    dependencies=[
        Depends(
            bloquear_escrita_administrativa_em_producao
        )
    ],
)
def obter_pedidos_administrativos(
    limite: int = 200,
):
    limite = max(1, min(limite, 500))
    return listar_pedidos_admin(limite)
