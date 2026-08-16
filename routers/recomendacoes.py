from fastapi import APIRouter

from models import PerfilPele, RespostaRecomendacoes
from services import gerar_recomendacoes


router = APIRouter(tags=["Recomendações"])


@router.post(
    "/recomendacoes",
    response_model=RespostaRecomendacoes,
)
def recomendar_por_perfil(
    perfil: PerfilPele,
):
    return gerar_recomendacoes(perfil)