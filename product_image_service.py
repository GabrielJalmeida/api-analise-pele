import re
import unicodedata

from io import BytesIO
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError
from config import obter_diretorio_media


MEDIA_PRODUTOS_DIR = (
    obter_diretorio_media()
    / "produtos"
)

CATEGORIAS_PERMITIDAS = {
    "limpeza",
    "hidratante",
    "serum",
    "protetor_solar",
    "outros",
}

FORMATOS_PERMITIDOS = {
    "JPEG",
    "PNG",
    "WEBP",
}

TAMANHO_MAXIMO_BYTES = 10 * 1024 * 1024
PIXELS_MAXIMOS = 40_000_000
DIMENSAO_MAXIMA = 1600


class ImagemProdutoInvalida(ValueError):
    pass


def gerar_slug(texto: str) -> str:
    texto_normalizado = unicodedata.normalize(
        "NFKD",
        texto,
    )

    texto_ascii = (
        texto_normalizado
        .encode("ascii", "ignore")
        .decode("ascii")
    )

    slug = re.sub(
        r"[^a-zA-Z0-9]+",
        "-",
        texto_ascii,
    )

    slug = slug.strip("-").lower()

    return slug or "produto"


def salvar_imagem_produto(
    conteudo: bytes,
    nome_produto: str,
    categoria: str,
) -> str:
    if categoria not in CATEGORIAS_PERMITIDAS:
        raise ImagemProdutoInvalida(
            "Categoria de produto inválida."
        )

    if not conteudo:
        raise ImagemProdutoInvalida(
            "A imagem está vazia."
        )

    if len(conteudo) > TAMANHO_MAXIMO_BYTES:
        raise ImagemProdutoInvalida(
            "A imagem não pode ultrapassar 10 MB."
        )

    try:
        with Image.open(BytesIO(conteudo)) as imagem:
            formato = imagem.format

            if formato not in FORMATOS_PERMITIDOS:
                raise ImagemProdutoInvalida(
                    "Formato de imagem não permitido."
                )

            largura, altura = imagem.size

            if largura * altura > PIXELS_MAXIMOS:
                raise ImagemProdutoInvalida(
                    "A resolução da imagem é muito alta."
                )

            imagem.load()

            imagem = ImageOps.exif_transpose(
                imagem
            )

            imagem.thumbnail(
                (
                    DIMENSAO_MAXIMA,
                    DIMENSAO_MAXIMA,
                ),
                Image.Resampling.LANCZOS,
            )

            if "A" in imagem.getbands():
                imagem_processada = imagem.convert(
                    "RGBA"
                )
            else:
                imagem_processada = imagem.convert(
                    "RGB"
                )

    except (
        UnidentifiedImageError,
        OSError,
    ) as erro:
        raise ImagemProdutoInvalida(
            "O arquivo enviado não é uma imagem válida."
        ) from erro

    pasta_categoria = (
        MEDIA_PRODUTOS_DIR
        / categoria
    )

    pasta_categoria.mkdir(
        parents=True,
        exist_ok=True,
    )

    slug = gerar_slug(nome_produto)

    identificador = uuid4().hex[:8]

    nome_arquivo = (
        f"{slug}-{identificador}.webp"
    )

    caminho_arquivo = (
        pasta_categoria
        / nome_arquivo
    )

    imagem_processada.save(
        caminho_arquivo,
        format="WEBP",
        quality=88,
        method=6,
    )

    return (
        f"/media/produtos/"
        f"{categoria}/"
        f"{nome_arquivo}"
    )


def remover_imagem_produto(
    imagem_url: str | None,
) -> None:
    if not imagem_url:
        return

    prefixo = "/media/produtos/"

    if not imagem_url.startswith(prefixo):
        return

    caminho_relativo = imagem_url.removeprefix(
        prefixo
    )

    caminho = (
        MEDIA_PRODUTOS_DIR
        / caminho_relativo
    ).resolve()

    raiz_media = (
        MEDIA_PRODUTOS_DIR.resolve()
    )

    if not caminho.is_relative_to(raiz_media):
        return

    if caminho.is_file():
        caminho.unlink()
