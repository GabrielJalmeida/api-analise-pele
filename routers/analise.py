from io import BytesIO

from fastapi import APIRouter, HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

from ai_service import interpretar_foto, interpretar_perfil
from models import (
    PerfilPele,
    RespostaAnaliseFotoInadequada,
    RespostaAnaliseFotoInsuficiente,
    RespostaAnaliseFotoSucesso,
    RespostaAnaliseTextoInsuficiente,
    RespostaRecomendacoes,
    TextoAnalisePele,
)
from services import (
    gerar_recomendacoes,
    obter_mensagem_inadequacao,
)


router = APIRouter(tags=["Análise de Pele"])


MIME_POR_FORMATO = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}

FORMATOS_IMAGEM_PERMITIDOS = {
    "JPEG",
    "PNG",
    "WEBP",
}

TIPOS_IMAGEM_PERMITIDOS = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

TAMANHO_MAXIMO_IMAGEM = 5 * 1024 * 1024
TOTAL_MAXIMO_PIXELS = 20_000_000

def sanitizar_imagem(
        conteudo: bytes,
        formato: str,
) -> bytes:
    with Image.open(BytesIO(conteudo)) as imagem:
        imagem = ImageOps.exif_transpose(imagem)

        imagem_limpa = imagem.copy()
        imagem_limpa.info.clear()

        if formato == "JPEG":
            imagem_limpa = imagem_limpa.convert("RGB")

        buffer = BytesIO()

        imagem_limpa.save(
            buffer,
            format=formato,
        )

        return buffer.getvalue()

@router.post(
    "/analise-texto",
    response_model=(
        RespostaRecomendacoes
        | RespostaAnaliseTextoInsuficiente
    ),
)
def analisar_texto(
    dados: TextoAnalisePele,
):
    resultado = interpretar_perfil(dados.texto)

    if resultado.tipo_pele is None:
        return {
            "status": "informacoes_insuficientes",
            "mensagem": (
                "Não foi possível identificar o tipo de pele "
                "com as informações fornecidas."
            ),
            "perfil": resultado,
            "total_recomendacoes": 0,
            "recomendacoes": {},
        }

    perfil = PerfilPele(
        tipo_pele=resultado.tipo_pele,
        sensivel=resultado.sensivel,
        tem_espinha=resultado.tem_espinha,
    )

    return gerar_recomendacoes(perfil)


@router.post(
    "/analise-foto",
    response_model=(
        RespostaAnaliseFotoSucesso
        | RespostaAnaliseFotoInadequada
        | RespostaAnaliseFotoInsuficiente
    ),
)
async def analisar_foto(
    arquivo: UploadFile,
):
    if arquivo.content_type not in TIPOS_IMAGEM_PERMITIDOS:
        raise HTTPException(
            status_code=415,
            detail=(
                "Formato de imagem não permitido. "
                "Envie uma imagem JPG, PNG ou WEBP."
            ),
        )

    conteudo = await arquivo.read(
        TAMANHO_MAXIMO_IMAGEM + 1
    )

    if len(conteudo) > TAMANHO_MAXIMO_IMAGEM:
        raise HTTPException(
            status_code=413,
            detail="A imagem não pode ultrapassar 5 MB.",
        )

    try:
        with Image.open(BytesIO(conteudo)) as imagem:
            formato_real = imagem.format
            largura, altura = imagem.size

            if largura * altura > TOTAL_MAXIMO_PIXELS:
                raise HTTPException(
                    status_code=413,
                    detail=(
                        "A imagem não pode ultrapassar "
                        "20 megapixels."
                    ),
                )

            imagem.verify()

    except HTTPException:
        raise

    except Image.DecompressionBombError:
        raise HTTPException(
            status_code=413,
            detail=(
                "As dimensões da imagem são grandes demais."
            ),
        )

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=415,
            detail=(
                "O arquivo enviado não é uma imagem válida."
            ),
        )

    if formato_real not in FORMATOS_IMAGEM_PERMITIDOS:
        raise HTTPException(
            status_code=415,
            detail=(
                "Formato de imagem não permitido. "
                "Envie uma imagem JPG, PNG ou WEBP."
            ),
        )

    mime_type_real = MIME_POR_FORMATO[formato_real]

    conteudo_sanitizado = sanitizar_imagem(
        conteudo,
        formato_real,
    )

    resultado = await run_in_threadpool(
        interpretar_foto,
        conteudo_sanitizado,
        mime_type_real,
    )

    if not resultado.imagem_adequada:
        return {
            "status": "imagem_inadequada",
            "mensagem": obter_mensagem_inadequacao(
                resultado.motivo_inadequacao
            ),
            "analise": resultado.model_dump(),
        }

    if resultado.tipo_pele is None:
        return {
            "status": "informacoes_insuficientes",
            "mensagem": (
                "A imagem foi analisada, mas não foi possível "
                "estimar o tipo de pele com segurança."
            ),
            "analise": resultado.model_dump(),
            "total_recomendacoes": 0,
            "recomendacoes": {},
        }

    perfil = PerfilPele(
        tipo_pele=resultado.tipo_pele,
        sensivel=None,
        tem_espinha=resultado.tem_espinha,
    )

    recomendacoes = gerar_recomendacoes(perfil)

    return {
        "status": "sucesso",
        "analise": resultado.model_dump(),
        **recomendacoes,
    }