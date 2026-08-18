import type {
  PerfilPele,
  RespostaAnaliseFoto,
  RespostaAnaliseTexto,
  RespostaRecomendacoes,
} from '../types/analise'

import {
  otimizarImagemParaAnalise,
} from './image'

const API_URL = import.meta.env.VITE_API_URL

interface ErroValidacao {
  msg?: string
}

interface RespostaErro {
  detail?: string
  mensagem?: string
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

    const primeiroErro = dados.erros?.[0]

    if (primeiroErro?.msg) {
      return primeiroErro.msg
    }
  } catch {
    // A resposta pode não possuir JSON válido.
  }

  return `Erro ${response.status}`
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
  const arquivoPreparado =
    await otimizarImagemParaAnalise(
      arquivo,
    )

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
