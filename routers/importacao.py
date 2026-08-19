from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from admin_security import (
    bloquear_escrita_administrativa_em_producao,
)
from catalog_ai_service import interpretar_catalogo
from catalog_import_service import (
    ArquivoCatalogoInvalido,
    TAMANHO_MAXIMO_ARQUIVO,
    confirmar_importacao,
    processar_arquivo_catalogo,
    validar_rascunhos,
)
from models import (
    ConfirmarImportacaoCatalogo,
    RespostaImportacaoCatalogo,
    RespostaPreviaImportacao,
    SolicitarInterpretacaoCatalogo,
)


router = APIRouter(
    prefix="/produtos/importacao",
    tags=["Importação de catálogo"],
    dependencies=[
        Depends(
            bloquear_escrita_administrativa_em_producao
        )
    ],
)


def _resposta_previa(
    resultado: dict,
    origem: str,
) -> dict:
    produtos = resultado["produtos"]
    erros = resultado["erros"]

    return {
        "status": "previa_pronta",
        "origem": origem,
        "total_linhas": resultado["total_linhas"],
        "total_validos": len(produtos),
        "total_erros": len(erros),
        "produtos": produtos,
        "erros": erros,
    }


@router.post(
    "/arquivo",
    response_model=RespostaPreviaImportacao,
)
async def criar_previa_arquivo(
    arquivo: UploadFile = File(...),
):
    try:
        conteudo = await arquivo.read(
            TAMANHO_MAXIMO_ARQUIVO + 1
        )
        resultado = processar_arquivo_catalogo(
            conteudo,
            arquivo.filename or "catalogo",
        )
    except ArquivoCatalogoInvalido as erro:
        raise HTTPException(
            status_code=400,
            detail=str(erro),
        ) from erro
    finally:
        await arquivo.close()

    return _resposta_previa(
        resultado,
        "arquivo",
    )


@router.post(
    "/ia",
    response_model=RespostaPreviaImportacao,
)
def criar_previa_ia(
    dados: SolicitarInterpretacaoCatalogo,
):
    interpretado = interpretar_catalogo(
        dados.texto
    )
    resultado = validar_rascunhos(
        [
            produto.model_dump()
            for produto in interpretado.produtos
        ]
    )

    return _resposta_previa(
        resultado,
        "ia",
    )


@router.post(
    "/confirmar",
    response_model=RespostaImportacaoCatalogo,
)
def importar_catalogo(
    dados: ConfirmarImportacaoCatalogo,
):
    return confirmar_importacao(dados)
