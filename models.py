import math
import re

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import Literal


class ModeloEstrito(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TextoAnalisePele(ModeloEstrito):
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

class ResultadoAnaliseFoto(ModeloEstrito):
    imagem_adequada: bool

    tipo_pele: Literal[
        "oleosa",
        "seca",
        "mista",
        "normal"
    ] | None = None

    confianca_tipo_pele: Literal[
        "alta",
        "media"
    ] | None = None

    tem_espinha: bool | None = None
    marcas_pos_acne: bool | None = None
    vermelhidao: bool | None = None
    descamacao: bool | None = None
    brilho_excessivo: bool | None = None

    motivo_inadequacao: Literal[
        "sem_rosto_visivel",
        "rosto_distante",
        "imagem_escura",
        "imagem_desfocada",
        "iluminacao_irregular",
        "pele_molhada",
        "interferencia_visual",
        "outro"
    ] | None = None

    @model_validator(mode="after")
    def resultado_consistente(self):
        caracteristicas = (
            self.tipo_pele,
            self.confianca_tipo_pele,
            self.tem_espinha,
            self.marcas_pos_acne,
            self.vermelhidao,
            self.descamacao,
            self.brilho_excessivo,
        )

        if self.imagem_adequada:
            if self.motivo_inadequacao is not None:
                raise ValueError(
                    "Uma imagem adequada não pode ter motivo de inadequação"
                )

            if (
                self.tipo_pele is None
                and self.confianca_tipo_pele is not None
            ):
                raise ValueError(
                    "Uma análise sem tipo de pele não pode informar confiança"
                )

            if (
                self.tipo_pele is not None
                and self.confianca_tipo_pele is None
            ):
                raise ValueError(
                    "Uma análise com tipo de pele deve informar confiança"
                )

        else:
            if self.motivo_inadequacao is None:
                raise ValueError(
                    "Uma imagem inadequada deve informar o motivo"
                )

            if any(
                valor is not None
                for valor in caracteristicas
            ):
                raise ValueError(
                    "Uma imagem inadequada não pode ter características de pele"
                )

        return self


class ResultadoAnaliseIA(ModeloEstrito):
    entrada_valida: bool

    motivo_invalidacao: Literal[
        "sujeito_nao_humano",
        "fora_do_dominio",
        "instrucao_adversarial",
        "outro"
    ] | None = None

    tipo_pele: Literal[
        "oleosa",
        "seca",
        "mista",
        "normal"
    ] | None = None

    sensivel: bool | None = None
    tem_espinha: bool | None = None

    @model_validator(mode="after")
    def resultado_consistente(self):
        caracteristicas = (
            self.tipo_pele,
            self.sensivel,
            self.tem_espinha,
        )

        if self.entrada_valida:
            if self.motivo_invalidacao is not None:
                raise ValueError(
                    "Uma entrada válida não pode ter motivo de invalidação"
                )

        else:
            if self.motivo_invalidacao is None:
                raise ValueError(
                    "Uma entrada inválida deve informar o motivo"
                )

            if any(
                valor is not None
                for valor in caracteristicas
            ):
                raise ValueError(
                    "Uma entrada inválida não pode gerar características de pele"
                )

        return self

class PerfilPele(ModeloEstrito):
    tipo_pele: Literal["oleosa", "seca", "mista", "normal"]
    sensivel: bool | None = None
    tem_espinha: bool | None = None

class ProdutoResposta(ModeloEstrito):
    id: int
    nome: str
    preco: float
    estoque: int
    marca: str
    descricao_curta: str
    imagem_url: str
    conteudo: str
    ativos_principais: str

    tipo_pele: Literal[
        "oleosa",
        "seca",
        "mista",
        "normal",
        "todos"
    ]

    pele_sensivel: bool
    indicado_para_espinha: bool
    ativo: bool

    categoria: Literal[
        "limpeza",
        "hidratante",
        "serum",
        "protetor_solar",
        "outros"
    ]

class ProdutoRecomendado(ProdutoResposta):
    score: int
    motivos_compatibilidade: list[str]

class RespostaRecomendacoes(ModeloEstrito):
    perfil: PerfilPele
    total_recomendacoes: int

    recomendacoes: dict[
        Literal[
            "limpeza",
            "hidratante",
            "serum",
            "protetor_solar",
            "outros"
        ],
        list[ProdutoRecomendado]
    ]

class RespostaAnaliseTextoInsuficiente(ModeloEstrito):
    status: Literal["informacoes_insuficientes"]
    mensagem: str
    perfil: ResultadoAnaliseIA
    total_recomendacoes: int

    recomendacoes: dict[
        Literal[
            "limpeza",
            "hidratante",
            "serum",
            "protetor_solar",
            "outros"
        ],
        list[ProdutoRecomendado]
    ]

class RespostaAnaliseTextoForaEscopo(ModeloEstrito):
    status: Literal["fora_escopo"]
    mensagem: str

    motivo: Literal[
        "sujeito_nao_humano",
        "fora_do_dominio",
        "instrucao_adversarial",
        "outro"
    ]

class RespostaAnaliseFotoInadequada(ModeloEstrito):
    status: Literal["imagem_inadequada"]
    mensagem: str
    analise: ResultadoAnaliseFoto

class RespostaAnaliseFotoInsuficiente(ModeloEstrito):
    status: Literal["informacoes_insuficientes"]
    mensagem: str
    analise: ResultadoAnaliseFoto
    total_recomendacoes: int

    recomendacoes: dict[
        Literal[
            "limpeza",
            "hidratante",
            "serum",
            "protetor_solar",
            "outros"
        ],
        list[ProdutoRecomendado]
    ]

class RespostaAnaliseFotoSucesso(RespostaRecomendacoes):
    status: Literal["sucesso"]
    analise: ResultadoAnaliseFoto

class RespostaAnaliseFotoConfirmacao(ModeloEstrito):
    status: Literal["confirmacao_necessaria"]
    mensagem: str
    analise: ResultadoAnaliseFoto

    sensivel: bool | None = None
    tem_espinha: bool | None = None

class NovoProduto(ModeloEstrito):
    nome: str
    preco: float

    categoria: Literal[
        "limpeza",
        "hidratante",
        "serum",
        "protetor_solar",
        "outros"
    ]

    tipo_pele: Literal[
        "oleosa",
        "seca",
        "mista",
        "normal",
        "todos"
    ]

    estoque: int = 0
    marca: str = ""
    descricao_curta: str = ""
    imagem_url: str = ""
    conteudo: str = ""
    ativos_principais: str = ""
    pele_sensivel: bool = False
    indicado_para_espinha: bool = False
    ativo: bool = True

    @field_validator("nome")
    @classmethod
    def nome_valido(cls, valor):
        valor = valor.strip()

        if len(valor) < 2:
            raise ValueError(
                "O nome do produto deve conter pelo menos 2 caracteres"
            )

        if len(valor) > 100:
            raise ValueError(
                "O nome do produto não pode ultrapassar 100 caracteres"
            )

        return valor

    @field_validator("marca")
    @classmethod
    def marca_valida(cls, valor):
        valor = valor.strip()

        if valor and len(valor) < 2:
            raise ValueError(
                "A marca deve conter pelo menos 2 caracteres"
            )

        if len(valor) > 60:
            raise ValueError(
                "A marca não pode ultrapassar 60 caracteres"
            )

        return valor

    @field_validator("descricao_curta")
    @classmethod
    def descricao_curta_valida(cls, valor):
        valor = valor.strip()

        if valor and len(valor) < 10:
            raise ValueError(
                "A descrição deve conter pelo menos 10 caracteres"
            )

        if len(valor) > 300:
            raise ValueError(
                "A descrição não pode ultrapassar 300 caracteres"
            )

        return valor

    @field_validator("imagem_url")
    @classmethod
    def imagem_url_valida(cls, valor):
        valor = valor.strip()

        if len(valor) > 500:
            raise ValueError(
                "A URL da imagem não pode ultrapassar 500 caracteres"
            )

        return valor

    @field_validator("conteudo")
    @classmethod
    def conteudo_valido(cls, valor):
        valor = valor.strip()

        if len(valor) > 30:
            raise ValueError(
                "O conteúdo não pode ultrapassar 30 caracteres"
            )

        return valor

    @field_validator("ativos_principais")
    @classmethod
    def ativos_principais_validos(cls, valor):
        valor = valor.strip()

        if valor and len(valor) < 2:
            raise ValueError(
                "Informe os principais ativos do produto"
            )

        if len(valor) > 200:
            raise ValueError(
                "Os ativos principais não podem ultrapassar 200 caracteres"
            )

        return valor

    @field_validator("preco")
    @classmethod
    def preco_valido(cls, valor):
        if not math.isfinite(valor) or valor <= 0:
            raise ValueError(
                "O preço deve ser um número finito maior do que zero"
            )

        return valor

    @field_validator("estoque")
    @classmethod
    def estoque_valido(cls, valor):
        if valor < 0:
            raise ValueError(
                "O estoque não pode ser negativo"
            )

        return valor

class AtualizarProduto(ModeloEstrito):
    nome: str | None = None
    marca: str | None = None
    descricao_curta: str | None = None
    imagem_url: str | None = None
    conteudo: str | None = None
    ativos_principais: str | None = None

    preco: float | None = None
    estoque: int | None = None

    categoria: Literal[
        "limpeza",
        "hidratante",
        "serum",
        "protetor_solar",
        "outros"
    ] | None = None

    tipo_pele: Literal[
        "oleosa",
        "seca",
        "mista",
        "normal",
        "todos"
    ] | None = None

    pele_sensivel: bool | None = None
    indicado_para_espinha: bool | None = None
    ativo: bool | None = None

    @field_validator("nome")
    @classmethod
    def nome_valido(cls, valor):
        if valor is not None:
            valor = valor.strip()

            if len(valor) < 2:
                raise ValueError(
                    "O nome do produto deve conter pelo menos 2 caracteres"
                )

            if len(valor) > 100:
                raise ValueError(
                    "O nome do produto não pode ultrapassar 100 caracteres"
                )

        return valor

    @field_validator("marca")
    @classmethod
    def marca_valida(cls, valor):
        if valor is not None:
            valor = valor.strip()

            if valor and len(valor) < 2:
                raise ValueError(
                    "A marca deve conter pelo menos 2 caracteres"
                )

            if len(valor) > 60:
                raise ValueError(
                    "A marca não pode ultrapassar 60 caracteres"
                )

        return valor

    @field_validator("descricao_curta")
    @classmethod
    def descricao_curta_valida(cls, valor):
        if valor is not None:
            valor = valor.strip()

            if valor and len(valor) < 10:
                raise ValueError(
                    "A descrição deve conter pelo menos 10 caracteres"
                )

            if len(valor) > 300:
                raise ValueError(
                    "A descrição não pode ultrapassar 300 caracteres"
                )

        return valor

    @field_validator("imagem_url")
    @classmethod
    def imagem_url_valida(cls, valor):
        if valor is not None:
            valor = valor.strip()

            if len(valor) > 500:
                raise ValueError(
                    "A URL da imagem não pode ultrapassar 500 caracteres"
                )

        return valor

    @field_validator("conteudo")
    @classmethod
    def conteudo_valido(cls, valor):
        if valor is not None:
            valor = valor.strip()

            if len(valor) > 30:
                raise ValueError(
                    "O conteúdo não pode ultrapassar 30 caracteres"
                )

        return valor

    @field_validator("ativos_principais")
    @classmethod
    def ativos_principais_validos(cls, valor):
        if valor is not None:
            valor = valor.strip()

            if valor and len(valor) < 2:
                raise ValueError(
                    "Informe os principais ativos do produto"
                )

            if len(valor) > 200:
                raise ValueError(
                    "Os ativos principais não podem ultrapassar 200 caracteres"
                )

        return valor

    @field_validator("preco")
    @classmethod
    def preco_valido(cls, valor):
        if (
            valor is not None
            and (
                not math.isfinite(valor)
                or valor <= 0
            )
        ):
            raise ValueError(
                "O preço deve ser um número finito maior do que zero"
            )

        return valor

    @field_validator("estoque")
    @classmethod
    def estoque_valido(cls, valor):
        if valor is not None and valor < 0:
            raise ValueError(
                "O estoque não pode ser negativo"
            )

        return valor

class RespostaProdutoDesativado(ModeloEstrito):
    status: Literal["produto_desativado"]
    mensagem: str
    id: int

class RespostaUploadImagemProduto(ModeloEstrito):
    status: Literal["imagem_salva"]
    imagem_url: str


class ProdutoImportacaoRascunho(ModeloEstrito):
    nome: str = ""
    marca: str = ""
    descricao_curta: str = ""
    imagem_url: str = ""
    conteudo: str = ""
    ativos_principais: str = ""
    preco: float | None = None
    estoque: int = 0
    categoria: Literal[
        "limpeza",
        "hidratante",
        "serum",
        "protetor_solar",
        "outros",
    ] | None = None
    tipo_pele: Literal[
        "oleosa",
        "seca",
        "mista",
        "normal",
        "todos",
    ] | None = None
    pele_sensivel: bool = False
    indicado_para_espinha: bool = False
    ativo: bool = True


class CatalogoInterpretado(ModeloEstrito):
    produtos: list[ProdutoImportacaoRascunho]

    @field_validator("produtos")
    @classmethod
    def quantidade_produtos_valida(cls, valor):
        if not valor:
            raise ValueError(
                "Nenhum produto foi identificado"
            )

        if len(valor) > 100:
            raise ValueError(
                "A IA aceita no máximo 100 produtos por lote"
            )

        return valor


class SolicitarInterpretacaoCatalogo(ModeloEstrito):
    texto: str

    @field_validator("texto")
    @classmethod
    def texto_catalogo_valido(cls, valor):
        valor = valor.strip()

        if len(valor) < 5:
            raise ValueError(
                "Envie informações de pelo menos um produto"
            )

        if len(valor) > 50_000:
            raise ValueError(
                "O texto não pode ultrapassar 50.000 caracteres"
            )

        return valor


class ConfirmarImportacaoCatalogo(ModeloEstrito):
    produtos: list[NovoProduto]
    duplicados: Literal[
        "ignorar",
        "atualizar",
    ] = "ignorar"

    @field_validator("produtos")
    @classmethod
    def lote_importacao_valido(cls, valor):
        if not valor:
            raise ValueError(
                "Nenhum produto válido foi enviado"
            )

        if len(valor) > 1000:
            raise ValueError(
                "O lote não pode ultrapassar 1.000 produtos"
            )

        nomes = [
            produto.nome.casefold()
            for produto in valor
        ]

        if len(nomes) != len(set(nomes)):
            raise ValueError(
                "O lote contém nomes de produtos duplicados"
            )

        return valor


class ErroImportacaoCatalogo(ModeloEstrito):
    linha: int
    campo: str
    mensagem: str


class RespostaPreviaImportacao(ModeloEstrito):
    status: Literal["previa_pronta"]
    origem: Literal["arquivo", "ia"]
    total_linhas: int
    total_validos: int
    total_erros: int
    produtos: list[NovoProduto]
    erros: list[ErroImportacaoCatalogo]


class RespostaImportacaoCatalogo(ModeloEstrito):
    status: Literal["importacao_concluida"]
    criados: int
    atualizados: int
    ignorados: int


class ItemPedidoEntrada(ModeloEstrito):
    produto_id: int
    quantidade: int = 1

    @field_validator("produto_id")
    @classmethod
    def produto_id_valido(cls, valor):
        if valor <= 0:
            raise ValueError(
                "O identificador do produto deve ser positivo"
            )

        return valor

    @field_validator("quantidade")
    @classmethod
    def quantidade_valida(cls, valor):
        if valor < 1 or valor > 10:
            raise ValueError(
                "A quantidade deve estar entre 1 e 10"
            )

        return valor


class NovoPedido(ModeloEstrito):
    cliente_token: str
    cliente_nome: str
    cliente_email: str
    consentimento_retencao: bool
    itens: list[ItemPedidoEntrada]

    @field_validator("cliente_token")
    @classmethod
    def cliente_token_valido(cls, valor):
        valor = valor.strip()

        if len(valor) < 32 or len(valor) > 128:
            raise ValueError(
                "O identificador do cliente é inválido"
            )

        if not re.fullmatch(
            r"[A-Za-z0-9._~-]+",
            valor,
        ):
            raise ValueError(
                "O identificador do cliente é inválido"
            )

        return valor

    @field_validator("cliente_nome")
    @classmethod
    def cliente_nome_valido(cls, valor):
        valor = " ".join(valor.split())

        if len(valor) < 2 or len(valor) > 100:
            raise ValueError(
                "O nome deve conter entre 2 e 100 caracteres"
            )

        return valor

    @field_validator("cliente_email")
    @classmethod
    def cliente_email_valido(cls, valor):
        valor = valor.strip().lower()

        if (
            len(valor) > 254
            or not re.fullmatch(
                r"[^\s@]+@[^\s@]+\.[^\s@]+",
                valor,
            )
        ):
            raise ValueError(
                "Informe um e-mail válido"
            )

        return valor

    @field_validator("consentimento_retencao")
    @classmethod
    def consentimento_obrigatorio(cls, valor):
        if valor is not True:
            raise ValueError(
                "É necessário aceitar a retenção do histórico por até 1 ano"
            )

        return valor

    @field_validator("itens")
    @classmethod
    def itens_validos(cls, valor):
        if not valor or len(valor) > 20:
            raise ValueError(
                "O pedido deve conter entre 1 e 20 produtos"
            )

        ids = [
            item.produto_id
            for item in valor
        ]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "O pedido contém produtos duplicados"
            )

        return valor


class ItemPedidoResposta(ModeloEstrito):
    produto_id: int | None
    nome_produto: str
    marca: str
    imagem_url: str
    preco_unitario: float
    quantidade: int
    subtotal: float


class PedidoResposta(ModeloEstrito):
    codigo: str
    cliente_nome: str
    cliente_email: str
    total: float
    status: Literal[
        "registrado",
        "cancelado",
    ]
    criado_em: datetime
    expira_em: datetime
    modo: Literal["demonstracao"] = "demonstracao"
    itens: list[ItemPedidoResposta]


class RespostaCriacaoPedido(ModeloEstrito):
    status: Literal["pedido_registrado"]
    mensagem: str
    pedido: PedidoResposta


class RespostaHistoricoPedidos(ModeloEstrito):
    retencao_dias: Literal[365] = 365
    total: int
    pedidos: list[PedidoResposta]


class RespostaExclusaoHistorico(ModeloEstrito):
    status: Literal["historico_excluido"]
    pedidos_removidos: int


class ConfiguracaoIAEntrada(ModeloEstrito):
    provedor: Literal[
        "gemini",
        "openai",
        "anthropic",
    ]
    modelo: str
    api_key: str | None = None
    pedidos_atualizam_estoque: bool = False

    @field_validator("modelo")
    @classmethod
    def modelo_valido(cls, valor):
        valor = valor.strip()

        if len(valor) < 2 or len(valor) > 120:
            raise ValueError(
                "O nome do modelo deve conter entre 2 e 120 caracteres"
            )

        return valor

    @field_validator("api_key")
    @classmethod
    def api_key_valida(cls, valor):
        if valor is None:
            return None

        valor = valor.strip()

        if not valor:
            return None

        if len(valor) < 8 or len(valor) > 500:
            raise ValueError(
                "A chave de API parece inválida"
            )

        return valor


class ConfiguracaoIAResposta(ModeloEstrito):
    provedor: Literal[
        "gemini",
        "openai",
        "anthropic",
    ]
    modelo: str
    api_key_configurada: bool
    pedidos_atualizam_estoque: bool
    armazenamento: Literal[
        "variaveis_de_ambiente",
        "arquivo_local",
    ]
