import type {
  AtualizarProduto,
  CategoriaProduto,
  FiltrosProdutos,
  NovoProduto,
  Pedido,
  PoliticaDuplicados,
  PreviaImportacao,
  Produto,
  ResultadoImportacao,
  RespostaUploadImagemProduto,
} from '../types/produto'

export const API_URL = (
  import.meta.env.VITE_API_URL
  ?? 'http://127.0.0.1:8000'
).replace(/\/$/, '')

export async function aguardarApiDisponivel(): Promise<void> {
  const tentativas = 8

  for (let tentativa = 1; tentativa <= tentativas; tentativa += 1) {
    try {
      const resposta = await fetch(`${API_URL}/status`, {
        cache: 'no-store',
      })

      if (resposta.ok) {
        return
      }
    } catch {
      // A API pode ainda estar iniciando ou retomando de um estado ocioso.
    }

    if (tentativa < tentativas) {
      await new Promise((resolve) => {
        window.setTimeout(resolve, 750)
      })
    }
  }

  throw new Error('A API não respondeu no tempo esperado.')
}

interface RespostaErroApi {
  detail?: string
  mensagem?: string
  erros?: Array<{
    campo?: string
    mensagem?: string
  }>
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

    if (dados.erros?.[0]?.mensagem) {
      const campo = dados.erros[0].campo
      mensagem = campo
        ? `${campo}: ${dados.erros[0].mensagem}`
        : dados.erros[0].mensagem
    }
  } catch {
    mensagem = `Erro ${resposta.status}`
  }

  throw new ErroApi(
    resposta.status,
    mensagem,
  )
}

export async function enviarImagemProduto(
  arquivo: File,
  nomeProduto: string,
  categoria: CategoriaProduto,
): Promise<RespostaUploadImagemProduto> {
  const formulario = new FormData()

  formulario.append(
    'arquivo',
    arquivo,
  )

  formulario.append(
    'nome_produto',
    nomeProduto.trim(),
  )

  formulario.append(
    'categoria',
    categoria,
  )

  const resposta = await fetch(
    `${API_URL}/produtos/imagem`,
    {
      method: 'POST',
      body: formulario,
    },
  )

  await validarResposta(resposta)

  return resposta.json()
}

export async function removerImagemProduto(
  imagemUrl: string,
): Promise<void> {
  const parametros = new URLSearchParams({
    imagem_url: imagemUrl,
  })

  const resposta = await fetch(
    `${API_URL}/produtos/imagem?${parametros}`,
    { method: 'DELETE' },
  )

  await validarResposta(resposta)
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

export async function criarPreviaArquivo(
  arquivo: File,
): Promise<PreviaImportacao> {
  const formulario = new FormData()
  formulario.append('arquivo', arquivo)

  const resposta = await fetch(
    `${API_URL}/produtos/importacao/arquivo`,
    {
      method: 'POST',
      body: formulario,
    },
  )

  await validarResposta(resposta)
  return resposta.json()
}
export async function criarPreviaComIa(
  texto: string,
): Promise<PreviaImportacao> {
  const resposta = await fetch(
    `${API_URL}/produtos/importacao/ia`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ texto }),
    },
  )

  await validarResposta(resposta)
  return resposta.json()
}

export async function confirmarImportacao(
  produtos: NovoProduto[],
  duplicados: PoliticaDuplicados,
): Promise<ResultadoImportacao> {
  const resposta = await fetch(
    `${API_URL}/produtos/importacao/confirmar`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        produtos,
        duplicados,
      }),
    },
  )

  await validarResposta(resposta)
  return resposta.json()
}

export async function buscarPedidos(): Promise<Pedido[]> {
  const resposta = await fetch(
    `${API_URL}/admin/pedidos`,
  )

  await validarResposta(resposta)
  return resposta.json()
}
