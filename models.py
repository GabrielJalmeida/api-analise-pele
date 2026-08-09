from pydantic import BaseModel, field_validator
from typing import Literal

class TextoAnalisePele(BaseModel):
    texto: str

    @field_validator("texto")
    @classmethod
    def texto_valido(cls, valor):
        valor = valor.strip()

        texto_sem_espacos = "".join(valor.split())

        if len(texto_sem_espacos) < 10:
            raise ValueError(
                "O texto deve conter pelo menos 10 caracteres úteis"
            )

        if len(valor) > 1000:
            raise ValueError(
                "O texto não pode ultrapassar 1000 caracteres"
            )

        return valor

class PerfilPele(BaseModel):
    tipo_pele: Literal["oleosa", "seca", "mista", "normal"]
    sensivel: bool
    tem_espinha: bool

class NovoProduto(BaseModel):
    nome: str
    preco: float
    estoque: int
    categoria: Literal["limpeza", "hidratante", "serum", "protetor_solar", "outros"]
    tipo_pele: Literal["oleosa", "seca", "mista", "normal", "todos"]
    pele_sensivel: bool
    indicado_para_espinha: bool
    ativo: bool = True

    @field_validator("nome")
    @classmethod
    def nome_valido(cls, valor):
        valor = valor.strip()

        if len(valor) < 2:
            raise ValueError("O nome do produto deve conter pelo menos 2 caracteres")
        if len(valor) > 100:
            raise ValueError("O nome do produto não pode ultrapassar 100 caracteres")
        
        return valor

    @field_validator("preco")
    @classmethod
    def preco_valido(cls, valor):
        if valor <= 0:
            raise ValueError("O preço deve ser maior do que zero")
        return valor

    @field_validator("estoque")
    @classmethod
    def estoque_valido(cls, valor):
        if valor < 0:
            raise ValueError("O estoque não pode ser negativo")
        return valor


class AtualizarProduto(BaseModel):
    nome: str | None = None
    preco: float | None = None
    estoque: int | None = None
    categoria: Literal["limpeza", "hidratante", "serum", "protetor_solar", "outros"] | None = None
    tipo_pele: Literal["oleosa", "seca", "mista", "normal", "todos"] | None = None
    pele_sensivel: bool | None = None
    indicado_para_espinha: bool | None = None
    ativo: bool | None = None

    @field_validator("nome")
    @classmethod
    def nome_valido(cls, valor):
        if valor is not None:
            valor = valor.strip()

            if len(valor) < 2:
                raise ValueError("O nome do produto deve conter pelo menos 2 caracteres")
            if len(valor) > 100:
                raise ValueError("O nome do produto não pode ultrapassar 100 caracteres")

        return valor

    @field_validator("preco")
    @classmethod
    def preco_valido(cls, valor):
        if valor is not None and valor <= 0:
            raise ValueError("O preço deve ser maior do que zero")
        return valor

    @field_validator("estoque")
    @classmethod
    def estoque_valido(cls, valor):
        if valor is not None and valor < 0:
            raise ValueError("O estoque não pode ser negativo")
        return valor
