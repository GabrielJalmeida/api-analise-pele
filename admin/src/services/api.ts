import type {
  AtualizarProduto,
  FiltrosProdutos,
  NovoProduto,
  Produto,
} from '../types/produto'

const API_URL = import.meta.env.VITE_API_URL

interface RespostaErroApi {
  detail?: string
  mensagem?: string
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

async function validarResposta(
  resposta: Response,
): Promise<void> {
  if (resposta.ok) {
    return
  }

  let mensagem = `Erro ${resposta.status}`

  try {
    const dados =
      (await resposta.json()) as RespostaErroApi

    if (typeof dados.detail === 'string') {
      mensagem = dados.detail
    } else if (typeof dados.mensagem === 'string') {
      mensagem = dados.mensagem
    }
  } catch {
    mensagem = `Erro ${resposta.status}`
  }

  throw new ErroApi(
    resposta.status,
    mensagem,
  )
}

export async function criarProduto(
  novoProduto: NovoProduto,
): Promise<Produto> {
  const resposta = await fetch(
    `${API_URL}/produto`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(novoProduto),
    },
  )

  await validarResposta(resposta)

  return resposta.json()
}

export async function buscarProdutos(
  filtros: FiltrosProdutos = {},
): Promise<Produto[]> {
  const parametros = new URLSearchParams()

  if (filtros.busca?.trim()) {
    parametros.set(
      'busca',
      filtros.busca.trim(),
    )
  }

  if (filtros.categoria) {
    parametros.set(
      'categoria',
      filtros.categoria,
    )
  }

  if (filtros.tipo_pele) {
    parametros.set(
      'tipo_pele',
      filtros.tipo_pele,
    )
  }

  if (filtros.ativo !== undefined) {
    parametros.set(
      'ativo',
      String(filtros.ativo),
    )
  }

  const query = parametros.toString()

  const url = query
    ? `${API_URL}/produtos?${query}`
    : `${API_URL}/produtos`

  const resposta = await fetch(url)

  await validarResposta(resposta)

  return resposta.json()
}

export async function desativarProduto(
  id: number,
): Promise<void> {
  const resposta = await fetch(
    `${API_URL}/produto/${id}`,
    {
      method: 'DELETE',
    },
  )

  await validarResposta(resposta)
}

export async function reativarProduto(
  id: number,
): Promise<Produto> {
  const resposta = await fetch(
    `${API_URL}/produto/${id}`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ativo: true,
      }),
    },
  )

  await validarResposta(resposta)

  return resposta.json()
}

export async function atualizarProduto(
  id: number,
  dados: AtualizarProduto,
): Promise<Produto> {
  const resposta = await fetch(
    `${API_URL}/produto/${id}`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dados),
    },
  )

  await validarResposta(resposta)

  return resposta.json()
}