from io import BytesIO

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    UploadFile,
)
from PIL import (
    Image,
    ImageOps,
    UnidentifiedImageError,
)
from starlette.concurrency import run_in_threadpool

from ai_service import (
    interpretar_foto,
    interpretar_perfil,
)
from models import (
    PerfilPele,
    RespostaAnaliseFotoInadequada,
    RespostaAnaliseFotoInsuficiente,
    RespostaAnaliseFotoSucesso,
    RespostaAnaliseTextoForaEscopo,
    RespostaAnaliseTextoInsuficiente,
    RespostaRecomendacoes,
    RespostaAnaliseFotoConfirmacao,
    TextoAnalisePele,
)
from services import (
    gerar_recomendacoes,
    obter_mensagem_inadequacao,
)


router = APIRouter(
    tags=["Análise de Pele"]
)


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

TAMANHO_MAXIMO_IMAGEM = (
    5 * 1024 * 1024
)

TOTAL_MAXIMO_PIXELS = (
    50_000_000
)

DIMENSAO_MAXIMA_ANALISE = 4096


def sanitizar_imagem(
    conteudo: bytes,
    formato: str,
) -> bytes:
    with Image.open(
        BytesIO(conteudo)
    ) as imagem:
        imagem = (
            ImageOps.exif_transpose(
                imagem
            )
        )

        imagem_limpa = imagem.copy()
        imagem_limpa.info.clear()

        imagem_limpa.thumbnail(
            (
                DIMENSAO_MAXIMA_ANALISE,
                DIMENSAO_MAXIMA_ANALISE,
            ),
            Image.Resampling.LANCZOS,
        )

        if formato == "JPEG":
            imagem_limpa = (
                imagem_limpa.convert(
                    "RGB"
                )
            )

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
        | RespostaAnaliseTextoForaEscopo
    ),
)
def analisar_texto(
    dados: TextoAnalisePele,
):
    resultado = interpretar_perfil(
        dados.texto
    )

    if not resultado.entrada_valida:
        return {
            "status": "fora_escopo",
            "mensagem": (
                "A descrição enviada não corresponde "
                "a uma análise cosmética de pele humana."
            ),
            "motivo": (
                resultado
                .motivo_invalidacao
            ),
        }

    if resultado.tipo_pele is None:
        return {
            "status":
                "informacoes_insuficientes",
            "mensagem": (
                "Não foi possível identificar "
                "o tipo de pele com as "
                "informações fornecidas."
            ),
            "perfil": resultado,
            "total_recomendacoes": 0,
            "recomendacoes": {},
        }

    perfil = PerfilPele(
        tipo_pele=resultado.tipo_pele,
        sensivel=resultado.sensivel,
        tem_espinha=(
            resultado.tem_espinha
        ),
    )

    return gerar_recomendacoes(
        perfil
    )


@router.post(
    "/analise-foto",
    response_model=(
        RespostaAnaliseFotoSucesso
        | RespostaAnaliseFotoInadequada
        | RespostaAnaliseFotoInsuficiente
        | RespostaAnaliseFotoConfirmacao
    ),
)
async def analisar_foto(
    arquivo: UploadFile,
    texto: str | None = Form(
        default=None,
    ),
):
    if (
        arquivo.content_type
        not in TIPOS_IMAGEM_PERMITIDOS
    ):
        raise HTTPException(
            status_code=415,
            detail=(
                "Formato de imagem não "
                "permitido. Envie uma imagem "
                "JPG, PNG ou WEBP."
            ),
        )

    texto_limpo = (
        texto.strip()
        if texto
        else None
    )

    if texto_limpo:
        if len(texto_limpo) < 10:
            raise HTTPException(
                status_code=422,
                detail=(
                    "A descrição complementar "
                    "deve possuir pelo menos "
                    "10 caracteres."
                ),
            )

        if len(texto_limpo) > 1000:
            raise HTTPException(
                status_code=422,
                detail=(
                    "A descrição complementar "
                    "não pode ultrapassar "
                    "1000 caracteres."
                ),
            )

    conteudo = await arquivo.read(
        TAMANHO_MAXIMO_IMAGEM + 1
    )

    if (
        len(conteudo)
        > TAMANHO_MAXIMO_IMAGEM
    ):
        raise HTTPException(
            status_code=413,
            detail=(
                "A imagem não pode "
                "ultrapassar 5 MB."
            ),
        )

    try:
        with Image.open(
            BytesIO(conteudo)
        ) as imagem:
            formato_real = imagem.format

            largura, altura = (
                imagem.size
            )

            if (
                largura * altura
                > TOTAL_MAXIMO_PIXELS
            ):
                raise HTTPException(
                    status_code=413,
                    detail=(
                        "A imagem não pode "
                        "ultrapassar "
                        "50 megapixels."
                    ),
                )

            imagem.verify()

    except HTTPException:
        raise

    except Image.DecompressionBombError:
        raise HTTPException(
            status_code=413,
            detail=(
                "As dimensões da imagem "
                "são grandes demais."
            ),
        )

    except (
        UnidentifiedImageError,
        OSError,
    ):
        raise HTTPException(
            status_code=415,
            detail=(
                "O arquivo enviado não é "
                "uma imagem válida."
            ),
        )

    if (
        formato_real
        not in FORMATOS_IMAGEM_PERMITIDOS
    ):
        raise HTTPException(
            status_code=415,
            detail=(
                "Formato de imagem não "
                "permitido. Envie uma imagem "
                "JPG, PNG ou WEBP."
            ),
        )

    mime_type_real = (
        MIME_POR_FORMATO[
            formato_real
        ]
    )

    conteudo_sanitizado = (
        sanitizar_imagem(
            conteudo,
            formato_real,
        )
    )

    resultado_foto = (
        await run_in_threadpool(
            interpretar_foto,
            conteudo_sanitizado,
            mime_type_real,
        )
    )

    if not resultado_foto.imagem_adequada:
        return {
            "status": "imagem_inadequada",
            "mensagem":
                obter_mensagem_inadequacao(
                    resultado_foto
                    .motivo_inadequacao
                ),
            "analise":
                resultado_foto.model_dump(),
        }

    resultado_texto = None

    if texto_limpo:
        resultado_texto = (
            await run_in_threadpool(
                interpretar_perfil,
                texto_limpo,
            )
        )

        if (
            not resultado_texto
            .entrada_valida
        ):
            resultado_texto = None

    sensivel = (
        resultado_texto.sensivel
        if resultado_texto
        else None
    )

    tem_espinha = (
        resultado_texto.tem_espinha
        if (
            resultado_texto
            and resultado_texto.tem_espinha
            is not None
        )
        else resultado_foto.tem_espinha
    )

    if (
        resultado_texto
        and resultado_foto.tipo_pele
        is not None
        and resultado_texto.tipo_pele
        is not None
        and resultado_foto.tipo_pele
        != resultado_texto.tipo_pele
    ):
        return {
            "status":
                "confirmacao_necessaria",
            "mensagem": (
                "Só precisamos confirmar uma "
                "informação antes de continuar."
            ),
            "analise":
                resultado_foto.model_dump(),
            "sensivel": sensivel,
            "tem_espinha": tem_espinha,
        }

    tipo_pele = (
        resultado_texto.tipo_pele
        if (
            resultado_texto
            and resultado_texto.tipo_pele
            is not None
        )
        else resultado_foto.tipo_pele
    )

    if tipo_pele is None:
        return {
            "status":
                "informacoes_insuficientes",
            "mensagem": (
                "A análise foi concluída, "
                "mas não foi possível estimar "
                "o tipo de pele com segurança."
            ),
            "analise":
                resultado_foto.model_dump(),
            "total_recomendacoes": 0,
            "recomendacoes": {},
        }

    perfil = PerfilPele(
        tipo_pele=tipo_pele,
        sensivel=sensivel,
        tem_espinha=tem_espinha,
    )

    recomendacoes = (
        gerar_recomendacoes(
            perfil
        )
    )

    return {
        "status": "sucesso",
        "analise":
            resultado_foto.model_dump(),
        **recomendacoes,
    }