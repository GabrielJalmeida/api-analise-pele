import pytest
from pydantic import ValidationError

from models import NovoProduto, PerfilPele, ResultadoAnaliseFoto


def dados_produto(**alteracoes):
    dados = {
        "nome": "Hidratante teste",
        "preco": 49.90,
        "estoque": 5,
        "categoria": "hidratante",
        "tipo_pele": "todos",
        "pele_sensivel": True,
        "indicado_para_espinha": False,
        "ativo": True,
    }
    dados.update(alteracoes)
    return dados


@pytest.mark.parametrize("preco", [float("nan"), float("inf"), float("-inf")])
def test_preco_nao_aceita_valores_nao_finitos(preco):
    with pytest.raises(ValidationError):
        NovoProduto(**dados_produto(preco=preco))


def test_campos_desconhecidos_nao_sao_ignorados():
    with pytest.raises(ValidationError):
        PerfilPele(
            tipo_pele="oleosa",
            sensivel=True,
            tem_espinha=False,
            campo_inexistente=True,
        )


def test_imagem_inadequada_exige_motivo():
    with pytest.raises(ValidationError):
        ResultadoAnaliseFoto(imagem_adequada=False)


def test_imagem_inadequada_nao_aceita_caracteristicas_de_pele():
    with pytest.raises(ValidationError):
        ResultadoAnaliseFoto(
            imagem_adequada=False,
            motivo_inadequacao="imagem_escura",
            tipo_pele="oleosa",
        )


def test_imagem_adequada_nao_aceita_motivo_de_inadequacao():
    with pytest.raises(ValidationError):
        ResultadoAnaliseFoto(
            imagem_adequada=True,
            motivo_inadequacao="imagem_desfocada",
        )
