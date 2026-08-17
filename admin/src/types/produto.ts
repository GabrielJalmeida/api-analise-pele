export type CategoriaProduto =
  | 'limpeza'
  | 'hidratante'
  | 'serum'
  | 'protetor_solar'
  | 'outros'

export type TipoPele =
  | 'oleosa'
  | 'seca'
  | 'mista'
  | 'normal'
  | 'todos'

export interface Produto {
  id: number

  nome: string
  marca: string
  descricao_curta: string
  imagem_url: string
  conteudo: string
  ativos_principais: string

  preco: number
  estoque: number

  categoria: CategoriaProduto
  tipo_pele: TipoPele

  pele_sensivel: boolean
  indicado_para_espinha: boolean
  ativo: boolean
}

export interface NovoProduto {
  nome: string
  marca: string
  descricao_curta: string
  imagem_url: string
  conteudo: string
  ativos_principais: string

  preco: number
  estoque: number

  categoria: CategoriaProduto
  tipo_pele: TipoPele

  pele_sensivel: boolean
  indicado_para_espinha: boolean
  ativo: boolean
}

export type AtualizarProduto =
  Partial<NovoProduto>

export interface FiltrosProdutos {
  busca?: string
  categoria?: CategoriaProduto
  tipo_pele?: TipoPele
  ativo?: boolean
}

export interface RespostaUploadImagemProduto {
  status: 'imagem_salva'
  imagem_url: string
}