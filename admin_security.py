from fastapi import HTTPException

from config import ambiente_producao


def bloquear_escrita_administrativa_em_producao():
    """Mantém a demonstração pública somente leitura.

    O painel desktop usa ``APP_ENV=desktop`` e, portanto, continua
    autorizado a administrar o catálogo local do próprio usuário.
    """
    if ambiente_producao():
        raise HTTPException(
            status_code=404,
            detail="Rota não disponível neste ambiente",
        )
