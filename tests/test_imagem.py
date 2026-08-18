from io import BytesIO

from PIL import Image

from routers.analise import (
    DIMENSAO_MAXIMA_ANALISE,
    sanitizar_imagem,
)


def test_sanitizar_imagem_remove_exif():
    buffer = BytesIO()

    imagem = Image.new(
        "RGB",
        (10, 10),
        "white",
    )

    exif = Image.Exif()
    exif[0x010E] = "metadado de teste"

    imagem.save(
        buffer,
        format="JPEG",
        exif=exif,
    )

    conteudo_original = buffer.getvalue()

    conteudo_sanitizado = sanitizar_imagem(
        conteudo_original,
        "JPEG",
    )

    with Image.open(
        BytesIO(conteudo_sanitizado)
    ) as imagem_sanitizada:
        assert not imagem_sanitizada.getexif()


def test_sanitizar_imagem_limita_dimensoes():
    buffer = BytesIO()

    Image.new(
        "RGB",
        (3000, 1500),
        "white",
    ).save(
        buffer,
        format="JPEG",
    )

    conteudo_sanitizado = sanitizar_imagem(
        buffer.getvalue(),
        "JPEG",
    )

    with Image.open(
        BytesIO(conteudo_sanitizado)
    ) as imagem_sanitizada:
        assert max(
            imagem_sanitizada.size
        ) == DIMENSAO_MAXIMA_ANALISE
