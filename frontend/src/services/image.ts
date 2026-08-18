const DIMENSAO_MAXIMA = 1600
const QUALIDADE_WEBP = 0.82
const LIMITE_SEM_REPROCESSAR =
  700 * 1024

function carregarImagem(
  arquivo: File,
): Promise<{
  imagem: HTMLImageElement
  url: string
}> {
  return new Promise(
    (resolve, reject) => {
      const url =
        URL.createObjectURL(arquivo)

      const imagem = new Image()

      imagem.decoding = 'async'

      imagem.onload = () => {
        resolve({
          imagem,
          url,
        })
      }

      imagem.onerror = () => {
        URL.revokeObjectURL(url)

        reject(
          new Error(
            'Não foi possível preparar a imagem.',
          ),
        )
      }

      imagem.src = url
    },
  )
}

function converterCanvas(
  canvas: HTMLCanvasElement,
): Promise<Blob | null> {
  return new Promise((resolve) => {
    canvas.toBlob(
      resolve,
      'image/webp',
      QUALIDADE_WEBP,
    )
  })
}

export async function otimizarImagemParaAnalise(
  arquivo: File,
): Promise<File> {
  let url: string | null = null

  try {
    const carregamento =
      await carregarImagem(arquivo)

    const imagem = carregamento.imagem
    url = carregamento.url

    const maiorDimensao = Math.max(
      imagem.naturalWidth,
      imagem.naturalHeight,
    )

    if (
      maiorDimensao <= DIMENSAO_MAXIMA
      && arquivo.size <=
        LIMITE_SEM_REPROCESSAR
    ) {
      return arquivo
    }

    const escala = Math.min(
      1,
      DIMENSAO_MAXIMA / maiorDimensao,
    )

    const largura = Math.max(
      1,
      Math.round(
        imagem.naturalWidth * escala,
      ),
    )

    const altura = Math.max(
      1,
      Math.round(
        imagem.naturalHeight * escala,
      ),
    )

    const canvas =
      document.createElement('canvas')

    canvas.width = largura
    canvas.height = altura

    const contexto =
      canvas.getContext('2d')

    if (!contexto) {
      return arquivo
    }

    contexto.imageSmoothingEnabled = true
    contexto.imageSmoothingQuality = 'high'

    contexto.drawImage(
      imagem,
      0,
      0,
      largura,
      altura,
    )

    const blob =
      await converterCanvas(canvas)

    if (
      !blob
      || blob.type !== 'image/webp'
      || blob.size >= arquivo.size
    ) {
      return arquivo
    }

    const nomeBase =
      arquivo.name.replace(
        /\.[^.]+$/,
        '',
      ) || 'foto-pele'

    return new File(
      [blob],
      `${nomeBase}.webp`,
      {
        type: 'image/webp',
        lastModified:
          arquivo.lastModified,
      },
    )
  } catch {
    // O backend ainda valida e prepara o
    // arquivo original caso o navegador não
    // consiga realizar a otimização local.
    return arquivo
  } finally {
    if (url) {
      URL.revokeObjectURL(url)
    }
  }
}
