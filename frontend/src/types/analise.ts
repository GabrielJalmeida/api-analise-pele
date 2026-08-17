export type TipoAnalise =
  | 'foto'
  | 'texto'
  | 'manual'

export type TipoPele =
  | 'oleosa'
  | 'seca'
  | 'mista'
  | 'normal'

export type ConfiancaTipoPele =
  | 'alta'
  | 'media'

export type CategoriaProduto =
  | 'limpeza'
  | 'hidratante'
  | 'serum'
  | 'protetor_solar'
  | 'outros'

export interface PerfilPele {
  tipo_pele: TipoPele
  sensivel: boolean | null
  tem_espinha: boolean | null
}

export interface ProdutoRecomendado {
  id: number
  nome: string
  preco: number
  estoque: number

  marca: string
  descricao_curta: string
  imagem_url: string
  conteudo: string
  ativos_principais: string

  tipo_pele:
    | TipoPele
    | 'todos'

  pele_sensivel: boolean
  indicado_para_espinha: boolean
  ativo: boolean

  categoria: CategoriaProduto

  score: number
  motivos_compatibilidade: string[]
}

export type RecomendacoesPorCategoria =
  Partial<
    Record<
      CategoriaProduto,
      ProdutoRecomendado[]
    >
  >

export interface RespostaRecomendacoes {
  perfil: PerfilPele
  total_recomendacoes: number
  recomendacoes: RecomendacoesPorCategoria
}

export interface RespostaTextoInsuficiente {
  status: 'informacoes_insuficientes'
  mensagem: string
  perfil: {
    tipo_pele: TipoPele | null
    sensivel: boolean | null
    tem_espinha: boolean | null
  }
  total_recomendacoes: 0
  recomendacoes: RecomendacoesPorCategoria
}

export interface RespostaAnaliseTextoForaEscopo {
  status: 'fora_escopo'

  mensagem: string

  motivo:
    | 'sujeito_nao_humano'
    | 'fora_do_dominio'
    | 'instrucao_adversarial'
    | 'outro'
}

export type RespostaAnaliseTexto =
  | RespostaRecomendacoes
  | RespostaTextoInsuficiente
  | RespostaAnaliseTextoForaEscopo

export type MotivoImagemInadequada =
  | 'sem_rosto_visivel'
  | 'rosto_distante'
  | 'imagem_escura'
  | 'imagem_desfocada'
  | 'iluminacao_irregular'
  | 'pele_molhada'
  | 'interferencia_visual'
  | 'outro'

export interface ResultadoAnaliseFoto {
  imagem_adequada: boolean

  tipo_pele: TipoPele | null
    confianca_tipo_pele:
    | ConfiancaTipoPele
    | null
  tem_espinha: boolean | null
  marcas_pos_acne: boolean | null
  vermelhidao: boolean | null
  descamacao: boolean | null
  brilho_excessivo: boolean | null

  motivo_inadequacao:
    | MotivoImagemInadequada
    | null
}

export interface RespostaAnaliseFotoInadequada {
  status: 'imagem_inadequada'
  mensagem: string
  analise: ResultadoAnaliseFoto
}

export interface RespostaAnaliseFotoInsuficiente {
  status: 'informacoes_insuficientes'
  mensagem: string
  analise: ResultadoAnaliseFoto
  total_recomendacoes: number
  recomendacoes: RecomendacoesPorCategoria
}

export interface RespostaAnaliseFotoConfirmacao {
  status: 'confirmacao_necessaria'
  mensagem: string
  analise: ResultadoAnaliseFoto
  sensivel: boolean | null
  tem_espinha: boolean | null
}

export interface RespostaAnaliseFotoSucesso
  extends RespostaRecomendacoes {
  status: 'sucesso'
  analise: ResultadoAnaliseFoto
}

export type RespostaAnaliseFoto =
  | RespostaAnaliseFotoSucesso
  | RespostaAnaliseFotoInadequada
  | RespostaAnaliseFotoInsuficiente
  | RespostaAnaliseFotoConfirmacao