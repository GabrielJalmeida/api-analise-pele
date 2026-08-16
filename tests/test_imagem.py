from io import BytesIO

from PIL import Image

from routers.analise import sanitizar_imagem


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