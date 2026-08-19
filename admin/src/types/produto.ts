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

export interface ErroImportacao {
  linha: number
  campo: string
  mensagem: string
}

export interface PreviaImportacao {
  status: 'previa_pronta'
  origem: 'arquivo' | 'ia'
  total_linhas: number
  total_validos: number
  total_erros: number
  produtos: NovoProduto[]
  erros: ErroImportacao[]
}

export interface ResultadoImportacao {
  status: 'importacao_concluida'
  criados: number
  atualizados: number
  ignorados: number
}

export type PoliticaDuplicados =
  | 'ignorar'
  | 'atualizar'

export interface ItemPedido {
  produto_id: number | null
  nome_produto: string
  marca: string
  imagem_url: string
  preco_unitario: number
  quantidade: number
  subtotal: number
}

export interface Pedido {
  codigo: string
  cliente_nome: string
  cliente_email: string
  total: number
  status: 'registrado' | 'cancelado'
  criado_em: string
  expira_em: string
  modo: 'demonstracao'
  itens: ItemPedido[]
}

export type ProvedorIA =
  | 'gemini'
  | 'openai'
  | 'anthropic'

export interface ConfiguracaoIA {
  provedor: ProvedorIA
  modelo: string
  api_key_configurada: boolean
  pedidos_atualizam_estoque: boolean
  armazenamento:
    | 'variaveis_de_ambiente'
    | 'arquivo_local'
}

export interface AtualizacaoConfiguracaoIA {
  provedor: ProvedorIA
  modelo: string
  api_key?: string
  pedidos_atualizam_estoque: boolean
}
