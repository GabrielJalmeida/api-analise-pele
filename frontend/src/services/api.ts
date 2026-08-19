import type {
  PerfilPele,
  RespostaAnaliseFoto,
  RespostaAnaliseTexto,
  RespostaCriacaoPedido,
  RespostaHistoricoPedidos,
  RespostaRecomendacoes,
} from '../types/analise'

import {
  otimizarImagemParaAnalise,
} from './image'

const API_URL = (
  import.meta.env.VITE_API_URL
  ?? 'http://127.0.0.1:8000'
).replace(/\/$/, '')

interface ErroValidacao {
  msg?: string
  mensagem?: string
}

interface RespostaErro {
  detail?: string
  mensagem?: string
  message?: string
  erros?: ErroValidacao[]
}

export class ErroApi extends Error {
  status: number

  constructor(
    status: number,
    mensagem: string,
  ) {
    super(mensagem)

    this.name = 'ErroApi'
    this.status = status
  }
}

async function obterMensagemErro(
  response: Response,
): Promise<string> {
  try {
    const dados =
      (await response.json()) as RespostaErro

    if (typeof dados.detail === 'string') {
      return dados.detail
    }

    if (typeof dados.mensagem === 'string') {
      return dados.mensagem
    }

    if (typeof dados.message === 'string') {
      if (response.status >= 500) {
        return 'O serviço demorou mais do que o esperado. Tente novamente em alguns instantes.'
      }

      return dados.message
    }

    const primeiroErro = dados.erros?.[0]

    if (
      primeiroErro?.mensagem
      || primeiroErro?.msg
    ) {
      return (
        primeiroErro.mensagem
        ?? primeiroErro.msg
        ?? 'Dados inválidos.'
      )
    }
  } catch {
    // A resposta pode não possuir JSON válido.
  }

  if (response.status >= 500) {
    return 'O serviço está temporariamente indisponível. Tente novamente em alguns instantes.'
  }

  return `Erro ${response.status}`
}

const CHAVE_TOKEN_CLIENTE =
  'lumina_skin_cliente_token'

let tokenVolatil: string | null = null

function criarTokenCliente(): string {
  if (typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }

  const bytes = new Uint8Array(24)
  crypto.getRandomValues(bytes)

  return Array.from(
    bytes,
    (byte) => byte.toString(16).padStart(2, '0'),
  ).join('')
}

export function obterTokenCliente(
  criar = false,
): string | null {
  let token = tokenVolatil

  try {
    token = localStorage.getItem(
      CHAVE_TOKEN_CLIENTE,
    ) ?? token
  } catch {
    // Alguns modos privados bloqueiam o armazenamento local.
  }

  if (token) {
    tokenVolatil = token
  }

  if (!token && criar) {
    token = criarTokenCliente()
    tokenVolatil = token

    try {
      localStorage.setItem(
        CHAVE_TOKEN_CLIENTE,
        token,
      )
    } catch {
      // O histórico dura somente até fechar a aba neste caso.
    }
  }

  return token
}

export async function analisarTexto(
  texto: string,
): Promise<RespostaAnaliseTexto> {
  const response = await fetch(
    `${API_URL}/analise-texto`,
    {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json',
      },

      body: JSON.stringify({
        texto,
      }),
    },
  )

  if (!response.ok) {
    const mensagem =
      await obterMensagemErro(response)

    throw new ErroApi(
      response.status,
      mensagem,
    )
  }

  return response.json()
}

export async function analisarFoto(
  arquivo: File,
  texto?: string,
): Promise<RespostaAnaliseFoto> {
  const [arquivoPreparado] = await Promise.all([
    otimizarImagemParaAnalise(arquivo),
    prepararServico().catch(() => undefined),
  ])

  const formulario = new FormData()

  formulario.append(
    'arquivo',
    arquivoPreparado,
  )

  if (texto?.trim()) {
    formulario.append(
      'texto',
      texto.trim(),
    )
  }

  const response = await fetch(
    `${API_URL}/analise-foto`,
    {
      method: 'POST',
      body: formulario,
    },
  )

  if (!response.ok) {
    const mensagem =
      await obterMensagemErro(response)

    throw new ErroApi(
      response.status,
      mensagem,
    )
  }

  return response.json()
}

export async function prepararServico(): Promise<void> {
  const controlador = new AbortController()
  const limite = window.setTimeout(
    () => controlador.abort(),
    20_000,
  )

  try {
    await fetch(`${API_URL}/status`, {
      cache: 'no-store',
      signal: controlador.signal,
    })
  } finally {
    window.clearTimeout(limite)
  }
}

export async function buscarRecomendacoes(
  perfil: PerfilPele,
): Promise<RespostaRecomendacoes> {
  const response = await fetch(
    `${API_URL}/recomendacoes`,
    {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json',
      },

      body: JSON.stringify(perfil),
    },
  )

  if (!response.ok) {
    const mensagem =
      await obterMensagemErro(response)

    throw new ErroApi(
      response.status,
      mensagem,
    )
  }

  return response.json()
}

export async function registrarPedido(
  nome: string,
  email: string,
  produtosIds: number[],
  consentimento: boolean,
): Promise<RespostaCriacaoPedido> {
  const token = obterTokenCliente(true)

  const response = await fetch(
    `${API_URL}/pedidos`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        cliente_token: token,
        cliente_nome: nome,
        cliente_email: email,
        consentimento_retencao: consentimento,
        itens: produtosIds.map((produtoId) => ({
          produto_id: produtoId,
          quantidade: 1,
        })),
      }),
    },
  )

  if (!response.ok) {
    throw new ErroApi(
      response.status,
      await obterMensagemErro(response),
    )
  }

  return response.json()
}

export async function buscarHistoricoPedidos(): Promise<RespostaHistoricoPedidos> {
  const token = obterTokenCliente()

  if (!token) {
    return {
      retencao_dias: 365,
      total: 0,
      pedidos: [],
    }
  }

  const response = await fetch(
    `${API_URL}/pedidos/historico`,
    {
      headers: {
        'X-Cliente-Token': token,
      },
    },
  )

  if (!response.ok) {
    throw new ErroApi(
      response.status,
      await obterMensagemErro(response),
    )
  }

  return response.json()
}

export async function excluirHistoricoPedidos(): Promise<number> {
  const token = obterTokenCliente()

  if (!token) {
    return 0
  }

  const response = await fetch(
    `${API_URL}/pedidos/historico`,
    {
      method: 'DELETE',
      headers: {
        'X-Cliente-Token': token,
      },
    },
  )

  if (!response.ok) {
    throw new ErroApi(
      response.status,
      await obterMensagemErro(response),
    )
  }

  const dados = await response.json() as {
    pedidos_removidos: number
  }

  return dados.pedidos_removidos
}
