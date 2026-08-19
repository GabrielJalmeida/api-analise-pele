import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AnimatePresence,
  motion,
  useReducedMotion,
} from 'motion/react'

import type {
  ResultadoAnaliseFoto,
} from '../types/analise'

interface PhotoObservationTransitionProps {
  analise: ResultadoAnaliseFoto
  onConcluir: () => void
}

interface Observacao {
  titulo: string
  descricao: string
}

function descreverCaracteristica(
  valor: boolean | null,
  positivo: string,
  negativo: string,
): string {
  if (valor === true) {
    return positivo
  }

  if (valor === false) {
    return negativo
  }

  return 'Sem evidência suficiente para avaliar'
}

function criarObservacoes(
  analise: ResultadoAnaliseFoto,
): Observacao[] {
  return [
    {
      titulo: 'Espinhas',
      descricao: descreverCaracteristica(
        analise.tem_espinha,
        'Espinhas aparentes na imagem',
        'Não observadas na imagem',
      ),
    },
    {
      titulo: 'Marcas pós-acne',
      descricao: descreverCaracteristica(
        analise.marcas_pos_acne,
        'Marcas aparentes na imagem',
        'Não observadas na imagem',
      ),
    },
    {
      titulo: 'Vermelhidão',
      descricao: descreverCaracteristica(
        analise.vermelhidao,
        'Vermelhidão aparente na imagem',
        'Não observada na imagem',
      ),
    },
    {
      titulo: 'Descamação',
      descricao: descreverCaracteristica(
        analise.descamacao,
        'Descamação aparente na imagem',
        'Não observada na imagem',
      ),
    },
    {
      titulo: 'Brilho',
      descricao: descreverCaracteristica(
        analise.brilho_excessivo,
        'Brilho excessivo aparente',
        'Não observado em excesso',
      ),
    },
  ]
}

function PhotoObservationTransition({
  analise,
  onConcluir,
}: PhotoObservationTransitionProps) {
  const reduzirMovimento =
    useReducedMotion()

  const observacoes = useMemo(
    () => criarObservacoes(analise),
    [analise],
  )

  const [
    indiceAtual,
    setIndiceAtual,
  ] = useState(0)

  useEffect(() => {
    if (
      indiceAtual <
      observacoes.length
    ) {
      const tempo = reduzirMovimento
        ? 220
        : 650

      const temporizador =
        window.setTimeout(() => {
          setIndiceAtual(
            (indice) => indice + 1,
          )
        }, tempo)

      return () => {
        window.clearTimeout(
          temporizador,
        )
      }
    }

    const temporizador =
      window.setTimeout(
        onConcluir,
        reduzirMovimento
          ? 100
          : 250,
      )

    return () => {
      window.clearTimeout(
        temporizador,
      )
    }
  }, [
    indiceAtual,
    observacoes.length,
    onConcluir,
    reduzirMovimento,
  ])

  const observacaoAtual =
    observacoes[indiceAtual]

  return (
    <section
      id="resultado-foto"
      className="bg-[#f7f5f1] px-6 py-24 lg:px-10 lg:py-32"
    >
      <motion.div
        className="mx-auto max-w-4xl text-center"
        initial={{
          opacity: 0,
        }}
        animate={{
          opacity: 1,
        }}
      >
        <p className="text-xs uppercase tracking-[0.3em] text-[#8b7964]">
          Leitura visual
        </p>

        <h2 className="mt-5 font-serif text-4xl text-[#0d1b2a] sm:text-5xl">
          Interpretando
          <span className="italic text-[#7f8f7a]">
            {' '}a imagem.
          </span>
        </h2>

        <div className="relative mt-16 flex min-h-[170px] items-center justify-center overflow-hidden">
          <AnimatePresence mode="wait">
            {observacaoAtual && (
              <motion.div
                key={indiceAtual}
                className="absolute w-full"
                initial={{
                  opacity: 0,
                  y: reduzirMovimento
                    ? 0
                    : 55,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                exit={{
                  opacity: 0,
                  y: reduzirMovimento
                    ? 0
                    : -55,
                }}
                transition={{
                  duration:
                    reduzirMovimento
                      ? 0.1
                      : 0.3,
                  ease: 'easeOut',
                }}
              >
                <p className="text-xs uppercase tracking-[0.24em] text-[#9a8a76]">
                  {observacaoAtual.titulo}
                </p>

                <p className="mt-4 font-serif text-2xl text-[#0d1b2a] sm:text-3xl">
                  {
                    observacaoAtual.descricao
                  }
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="mt-8 flex justify-center gap-2">
          {observacoes.map(
            (_, indice) => (
              <span
                key={indice}
                className={`
                  h-1 rounded-full
                  transition-all
                  ${
                    indice <= indiceAtual
                      ? 'w-7 bg-[#a9b6a2]'
                      : 'w-3 bg-[#ddd6cc]'
                  }
                `}
              />
            ),
          )}
        </div>

        <p className="mt-8 text-xs text-[#90938c]">
          A leitura considera apenas o que é
          visualmente observável nesta imagem.
        </p>

        <button
          type="button"
          onClick={onConcluir}
          className="mt-6 text-xs text-[#777d75] underline decoration-[#b8b0a5] underline-offset-4 transition-colors hover:text-[#0d1b2a]"
        >
          Ver resultado agora
        </button>
      </motion.div>
    </section>
  )
}

export default PhotoObservationTransition
