from fastapi import HTTPException

from config import ambiente_producao


def bloquear_escrita_administrativa_em_producao():
    """Mantém a demonstração pública somente leitura.

    O painel web local usa ``APP_ENV=development``. Uma publicação
    do painel exige autenticação e autorização antes de liberar
    estas rotas em produção.
    """
    if ambiente_producao():
        raise HTTPException(
            status_code=404,
            detail="Rota não disponível neste ambiente",
        )
