import {
  useCallback,
  useEffect,
  useState,
} from 'react'

import { motion } from 'motion/react'

import PhotoObservationTransition from './PhotoObservationTransition'

import {
  buscarRecomendacoes,
  ErroApi,
} from '../services/api'

import type {
  CategoriaProduto,
  RespostaAnaliseFoto,
  RespostaAnaliseFotoSucesso,
  TipoPele,
} from '../types/analise'

interface PhotoResultProps {
  resultado: RespostaAnaliseFoto
}

const API_URL = (
  import.meta.env.VITE_API_URL ?? ''
).replace(/\/$/, '')

function montarUrlImagem(
  imagemUrl: string,
): string {
  if (
    imagemUrl.startsWith('http://')
    || imagemUrl.startsWith('https://')
  ) {
    return imagemUrl
  }

  return `${API_URL}${imagemUrl}`
}

const nomesPerfil: Record<
  TipoPele,
  string
> = {
  oleosa: 'Predominância de oleosidade',
  seca: 'Tendência ao ressecamento',
  mista: 'Características combinadas',
  normal: 'Perfil equilibrado',
}

const nomesCategorias: Record<
  CategoriaProduto,
  string
> = {
  limpeza: 'Limpeza',
  hidratante: 'Hidratação',
  serum: 'Séruns',
  protetor_solar: 'Proteção solar',
  outros: 'Outros cuidados',
}

const ordemCategorias: CategoriaProduto[] = [
  'limpeza',
  'hidratante',
  'serum',
  'protetor_solar',
  'outros',
]

const opcoesTipoPele: {
  tipo: TipoPele
  nome: string
  descricao: string
}[] = [
    {
      tipo: 'oleosa',
      nome: 'Oleosa',
      descricao:
        'Costuma apresentar brilho e oleosidade ao longo do dia.',
    },
    {
      tipo: 'seca',
      nome: 'Seca',
      descricao:
        'Costuma apresentar ressecamento, repuxamento ou pouca oleosidade.',
    },
    {
      tipo: 'mista',
      nome: 'Mista',
      descricao:
        'Algumas regiões ficam oleosas enquanto outras tendem ao ressecamento.',
    },
    {
      tipo: 'normal',
      nome: 'Normal',
      descricao:
        'Costuma manter equilíbrio, sem excesso frequente de oleosidade ou ressecamento.',
    },
  ]

function formatarPreco(
  preco: number,
) {
  return new Intl.NumberFormat(
    'pt-BR',
    {
      style: 'currency',
      currency: 'BRL',
    },
  ).format(preco)
}

function traduzirMotivo(
  motivo: string,
) {
  const motivos: Record<string, string> = {
    'Compatível com o tipo de pele identificado':
      'Compatível com o perfil estimado',

    'Indicado para pele com espinhas':
      'Selecionado considerando características do perfil',

    'Indicado para diferentes tipos de pele':
      'Uma opção versátil para diferentes perfis',

    'Adequado para pele sensível':
      'Compatível com perfis que exigem cuidados mais delicados',
  }

  return motivos[motivo] ?? motivo
}

function PhotoResult({
  resultado,
}: PhotoResultProps) {
  const [
    transicaoConcluida,
    setTransicaoConcluida,
  ] = useState(
    resultado.status ===
    'imagem_inadequada',
  )

  const [
    resultadoConfirmado,
    setResultadoConfirmado,
  ] = useState<
    RespostaAnaliseFotoSucesso | null
  >(null)

  const [
    confirmando,
    setConfirmando,
  ] = useState(false)

  const [
    erroConfirmacao,
    setErroConfirmacao,
  ] = useState<string | null>(null)

  useEffect(() => {
    setTransicaoConcluida(
      resultado.status ===
      'imagem_inadequada',
    )

    setResultadoConfirmado(null)
    setConfirmando(false)
    setErroConfirmacao(null)
  }, [resultado])

  const concluirTransicao =
    useCallback(() => {
      setTransicaoConcluida(true)
    }, [])

  async function confirmarTipoPele(
    tipoPele: TipoPele,
  ) {
    if (
      resultado.status !==
      'confirmacao_necessaria'
    ) {
      return
    }

    try {
      setConfirmando(true)
      setErroConfirmacao(null)

      const recomendacoes =
        await buscarRecomendacoes({
          tipo_pele: tipoPele,
          sensivel: resultado.sensivel,
          tem_espinha:
            resultado.tem_espinha,
        })

      setResultadoConfirmado({
        status: 'sucesso',
        analise: resultado.analise,
        ...recomendacoes,
      })
    } catch (erroRecebido) {
      if (
        erroRecebido instanceof ErroApi
      ) {
        setErroConfirmacao(
          erroRecebido.message,
        )
        return
      }

      if (
        erroRecebido instanceof TypeError
      ) {
        setErroConfirmacao(
          'Não foi possível conectar ao serviço. Tente novamente em alguns instantes.',
        )
        return
      }

      setErroConfirmacao(
        'Não foi possível concluir a recomendação.',
      )
    } finally {
      setConfirmando(false)
    }
  }

  /*
   * Imagens inadequadas não possuem
   * características confiáveis para animar.
   */
  if (
    resultado.status ===
    'imagem_inadequada'
  ) {
    return (
      <section
        id="resultado-foto"
        className="bg-[#f7f5f1] px-6 py-24 lg:px-10 lg:py-32"
      >
        <motion.div
          className="mx-auto max-w-5xl rounded-[2.5rem] border border-[#ded8cf] bg-white/60 p-8 sm:p-12 lg:p-14"
          initial={{
            opacity: 0,
            y: 24,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.7,
            ease: 'easeOut',
          }}
        >
          <p className="text-xs uppercase tracking-[0.28em] text-[#8b7964]">
            Não conseguimos usar esta imagem
          </p>

          <h2 className="mt-5 max-w-2xl font-serif text-4xl leading-tight tracking-[-0.03em] text-[#0d1b2a] sm:text-5xl">
            Vamos tentar com

            <span className="block italic text-[#7f8f7a]">
              uma foto melhor.
            </span>
          </h2>

          <p className="mt-6 max-w-2xl text-sm leading-7 text-[#646864] sm:text-base">
            {resultado.mensagem}
          </p>

          <div className="mt-10 grid gap-3 border-t border-[#e0dad2] pt-8 sm:grid-cols-3">
            {[
              'Rosto bem visível',
              'Iluminação uniforme',
              'Sem filtros ou interferências',
            ].map((dica) => (
              <div
                key={dica}
                className="rounded-2xl bg-[#f1ede6] px-5 py-4 text-sm text-[#686c66]"
              >
                {dica}
              </div>
            ))}
          </div>

          <a
            href="#experiencia-analise"
            className="mt-8 inline-flex rounded-full bg-[#0d1b2a] px-7 py-3.5 text-sm font-medium text-white transition-transform hover:-translate-y-0.5"
          >
            Escolher outra foto
          </a>
        </motion.div>
      </section>
    )
  }

  /*
   * Primeiro exibimos as observações
   * visuais que vieram da fotografia.
   */
  if (!transicaoConcluida) {
    return (
      <PhotoObservationTransition
        analise={resultado.analise}
        onConcluir={concluirTransicao}
      />
    )
  }

  /*
   * Imagem válida, mas sem informação
   * suficiente para estimar o tipo de pele.
   */
  if (
    resultado.status ===
    'informacoes_insuficientes'
  ) {
    return (
      <section
        id="resultado-foto"
        className="bg-[#f7f5f1] px-6 py-24 lg:px-10 lg:py-32"
      >
        <motion.div
          className="mx-auto max-w-5xl rounded-[2.5rem] border border-[#ded8cf] bg-white/60 p-8 sm:p-12 lg:p-14"
          initial={{
            opacity: 0,
            y: 20,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
        >
          <p className="text-xs uppercase tracking-[0.28em] text-[#8b7964]">
            Análise visual concluída
          </p>

          <h2 className="mt-5 max-w-3xl font-serif text-4xl leading-tight text-[#0d1b2a] sm:text-5xl">
            Ainda não conseguimos estimar

            <span className="block italic text-[#7f8f7a]">
              seu perfil com segurança.
            </span>
          </h2>

          <p className="mt-6 max-w-2xl text-sm leading-7 text-[#646864]">
            {resultado.mensagem}
          </p>

          <p className="mt-5 max-w-2xl text-xs leading-6 text-[#8a8d87]">
            Iluminação, ângulo, resolução e outras
            características da imagem podem alterar
            a leitura visual.
          </p>

          <a
            href="#experiencia-analise"
            className="mt-8 inline-flex rounded-full bg-[#0d1b2a] px-7 py-3.5 text-sm font-medium text-white"
          >
            Tentar outra foto
          </a>
        </motion.div>
      </section>
    )
  }

  /*
   * Foto e descrição produziram tipos
   * diferentes. O usuário confirma apenas
   * o comportamento habitual da própria pele.
   */
  if (
    resultado.status ===
    'confirmacao_necessaria' &&
    !resultadoConfirmado
  ) {
    return (
      <section
        id="resultado-foto"
        className="bg-[#f7f5f1] px-6 py-24 lg:px-10 lg:py-32"
      >
        <motion.div
          className="mx-auto max-w-5xl"
          initial={{
            opacity: 0,
            y: 24,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.65,
            ease: 'easeOut',
          }}
        >
          <p className="text-xs uppercase tracking-[0.28em] text-[#8b7964]">
            Só uma confirmação
          </p>

          <h2 className="mt-5 max-w-3xl font-serif text-4xl leading-tight tracking-[-0.03em] text-[#0d1b2a] sm:text-5xl">
            Como sua pele costuma

            <span className="block italic text-[#7f8f7a]">
              se comportar na maior parte dos dias?
            </span>
          </h2>

          <p className="mt-6 max-w-2xl text-sm leading-7 text-[#646864] sm:text-base">
            A aparência da pele pode variar de
            acordo com o momento da foto. Escolha
            a opção que melhor representa seu
            comportamento habitual.
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            {opcoesTipoPele.map(
              (opcao) => (
                <motion.button
                  key={opcao.tipo}
                  type="button"
                  disabled={confirmando}
                  onClick={() =>
                    confirmarTipoPele(
                      opcao.tipo,
                    )
                  }
                  className="
                    group rounded-[2rem]
                    border border-[#ded8cf]
                    bg-white/60
                    p-6 text-left
                    transition-colors
                    hover:border-[#a9b6a2]
                    hover:bg-white/90
                    disabled:cursor-not-allowed
                    disabled:opacity-50
                    sm:p-7
                  "
                  whileHover={
                    confirmando
                      ? undefined
                      : {
                        y: -3,
                      }
                  }
                  whileTap={
                    confirmando
                      ? undefined
                      : {
                        scale: 0.99,
                      }
                  }
                >
                  <div className="flex items-start justify-between gap-6">
                    <div>
                      <p className="font-serif text-2xl text-[#0d1b2a]">
                        {opcao.nome}
                      </p>

                      <p className="mt-3 max-w-sm text-sm leading-6 text-[#747872]">
                        {
                          opcao.descricao
                        }
                      </p>
                    </div>

                    <span
                      className="
                        flex h-9 w-9 shrink-0
                        items-center justify-center
                        rounded-full
                        border border-[#d7d0c7]
                        text-[#8b7964]
                        transition-colors
                        group-hover:border-[#a9b6a2]
                        group-hover:bg-[#eef1eb]
                      "
                    >
                      →
                    </span>
                  </div>
                </motion.button>
              ),
            )}
          </div>

          {confirmando && (
            <motion.div
              className="mt-6 flex items-center gap-4 rounded-2xl border border-[#d7ddd3] bg-[#eef1eb] px-5 py-5"
              initial={{
                opacity: 0,
                y: 8,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
            >
              <motion.span
                className="h-2.5 w-2.5 rounded-full bg-[#879681]"
                animate={{
                  opacity: [
                    0.35,
                    1,
                    0.35,
                  ],
                  scale: [
                    0.9,
                    1.1,
                    0.9,
                  ],
                }}
                transition={{
                  duration: 1.2,
                  repeat: Infinity,
                }}
              />

              <div>
                <p className="text-sm font-medium text-[#0d1b2a]">
                  Preparando suas recomendações
                </p>

                <p className="mt-1 text-xs leading-5 text-[#777b75]">
                  Estamos selecionando os
                  produtos compatíveis com o
                  perfil confirmado.
                </p>
              </div>
            </motion.div>
          )}

          {erroConfirmacao && (
            <motion.div
              className="mt-6 rounded-2xl border border-[#d8b8ae] bg-[#f8ebe7] px-5 py-4"
              initial={{
                opacity: 0,
                y: 8,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
            >
              <p className="text-sm leading-6 text-[#76534b]">
                {erroConfirmacao}
              </p>
            </motion.div>
          )}

          <p className="mt-8 max-w-2xl text-xs leading-6 text-[#8a8d87]">
            Essa confirmação não realiza uma nova
            análise por inteligência artificial.
            Ela apenas define qual perfil deve ser
            usado para selecionar os produtos.
          </p>
        </motion.div>
      </section>
    )
  }

  /*
   * Depois da confirmação, transformamos a
   * resposta de /recomendacoes em um resultado
   * de foto completo para reutilizar a mesma UI.
   */
  let resultadoFinal:
    RespostaAnaliseFotoSucesso

  if (resultadoConfirmado) {
    resultadoFinal =
      resultadoConfirmado
  } else if (
    resultado.status === 'sucesso'
  ) {
    resultadoFinal = resultado
  } else {
    return null
  }

  const categoriasDisponiveis =
    ordemCategorias.filter(
      (categoria) =>
        resultadoFinal.recomendacoes[
          categoria
        ]?.length,
    )

  return (
    <section
      id="resultado-foto"
      className="bg-[#f7f5f1] px-6 py-24 lg:px-10 lg:py-32"
    >
      <div className="mx-auto max-w-7xl">
        <motion.div
          className="grid gap-12 border-b border-[#dcd5cc] pb-16 lg:grid-cols-[0.9fr_1.1fr] lg:items-end"
          initial={{
            opacity: 0,
            y: 24,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.7,
            ease: 'easeOut',
          }}
        >
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[#8b7964]">
              Análise concluída
            </p>

            <h2 className="mt-5 font-serif text-4xl leading-tight tracking-[-0.03em] text-[#0d1b2a] sm:text-5xl lg:text-6xl">
              Encontramos cuidados

              <span className="block italic text-[#7f8f7a]">
                para o perfil estimado.
              </span>
            </h2>
          </div>

          <div className="lg:justify-self-end">
            <p className="text-xs uppercase tracking-[0.24em] text-[#8b7964]">
              Perfil considerado
            </p>

            <p className="mt-3 font-serif text-2xl text-[#0d1b2a]">
              {
                nomesPerfil[
                resultadoFinal.perfil
                  .tipo_pele
                ]
              }
            </p>

            <p className="mt-4 max-w-lg text-sm leading-7 text-[#696d68]">
              Esta seleção considera a análise
              da imagem e, quando fornecidas,
              informações sobre o comportamento
              habitual da sua pele.
            </p>
          </div>
        </motion.div>

        <motion.div
          className="mt-10 flex items-center justify-between gap-6"
          initial={{
            opacity: 0,
          }}
          animate={{
            opacity: 1,
          }}
          transition={{
            delay: 0.2,
          }}
        >
          <p className="text-sm text-[#656963]">
            {
              resultadoFinal
                .total_recomendacoes
            }{' '}
            {resultadoFinal
              .total_recomendacoes === 1
              ? 'produto selecionado'
              : 'produtos selecionados'}
          </p>

          <span className="text-xs text-[#95978f]">
            Catálogo Lumina
          </span>
        </motion.div>

        <div className="mt-16 space-y-20">
          {categoriasDisponiveis.map(
            (categoria) => {
              const produtos =
                resultadoFinal
                  .recomendacoes[
                categoria
                ] ?? []

              return (
                <div key={categoria}>
                  <div className="mb-7 flex items-end justify-between border-b border-[#e0dad2] pb-4">
                    <h3 className="font-serif text-2xl text-[#0d1b2a] sm:text-3xl">
                      {
                        nomesCategorias[
                        categoria
                        ]
                      }
                    </h3>

                    <span className="text-xs text-[#92948d]">
                      {produtos.length}{' '}
                      {produtos.length === 1
                        ? 'seleção'
                        : 'seleções'}
                    </span>
                  </div>

                  <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                    {produtos.map(
                      (
                        produto,
                        indice,
                      ) => (
                        <motion.article
                          key={produto.id}
                          className="
  group relative
  overflow-hidden
  rounded-[2rem]
  border border-[#ded8cf]
  bg-[#fbfaf7]
  p-7 sm:p-8
"
                          initial={{
                            opacity: 0,
                            y: 24,
                          }}
                          animate={{
                            opacity: 1,
                            y: 0,
                          }}
                          transition={{
                            duration: 0.6,
                            delay:
                              0.15 +
                              indice *
                              0.08,
                          }}
                          whileHover={{
                            y: -4,
                          }}
                        >
                          <div className="-mx-7 -mt-7 mb-7 overflow-hidden rounded-t-[2rem] bg-[#f1eee8] sm:-mx-8 sm:-mt-8">
                            <div className="aspect-[4/3] w-full">
                              <img
                                src={montarUrlImagem(
                                  produto.imagem_url,
                                )}
                                alt={produto.nome}
                                loading="lazy"
                                className="
        h-full w-full
        object-contain
        p-6
        transition-transform
        duration-500
        group-hover:scale-[1.03]
      "
                              />
                            </div>
                          </div>
                          <p className="text-xs uppercase tracking-[0.2em] text-[#8b7964]">
                            {
                              nomesCategorias[
                              produto
                                .categoria
                              ]
                            }
                          </p>

                          <h4 className="mt-10 font-serif text-2xl leading-tight text-[#0d1b2a]">
                            {
                              produto.nome
                            }
                          </h4>

                          <p className="mt-4 text-lg text-[#0d1b2a]">
                            {formatarPreco(
                              produto.preco,
                            )}
                          </p>

                          <div className="mt-8 space-y-3 border-t border-[#e4dfd8] pt-6">
                            {produto.motivos_compatibilidade.map(
                              (
                                motivo,
                                indiceMotivo,
                              ) => (
                                <div
                                  key={`${produto.id}-${indiceMotivo}`}
                                  className="flex gap-3"
                                >
                                  <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-[#a9b6a2]" />

                                  <p className="text-xs leading-6 text-[#72766f]">
                                    {traduzirMotivo(
                                      motivo,
                                    )}
                                  </p>
                                </div>
                              ),
                            )}
                          </div>
                        </motion.article>
                      ),
                    )}
                  </div>
                </div>
              )
            },
          )}
        </div>

        <p className="mx-auto mt-20 max-w-2xl text-center text-xs leading-6 text-[#8a8d87]">
          A análise tem finalidade informativa e
          cosmética. A estimativa pode variar de
          acordo com iluminação, ângulo, resolução,
          qualidade da imagem e informações
          fornecidas, e não representa diagnóstico
          médico.
        </p>
      </div>
    </section>
  )
}

export default PhotoResult