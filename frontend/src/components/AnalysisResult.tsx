import { motion } from 'motion/react'

import RecommendationsRoutine from './RecommendationsRoutine'

import type {
  RespostaAnaliseTexto,
} from '../types/analise'

interface AnalysisResultProps {
  resultado: RespostaAnaliseTexto
}

const nomesPerfil = {
  oleosa: 'Predominância de oleosidade',
  seca: 'Tendência ao ressecamento',
  mista: 'Características combinadas',
  normal: 'Perfil equilibrado',
}

function AnalysisResult({
  resultado,
}: AnalysisResultProps) {

  if (
    'status' in resultado &&
    resultado.status === 'fora_escopo'
  ) {
    return (
      <section
        id="resultado-analise"
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
            duration: 0.7,
            ease: 'easeOut',
          }}
        >
          <div className="rounded-[2.5rem] border border-[#ded8cf] bg-white/60 p-8 sm:p-12 lg:p-14">
            <p className="text-xs uppercase tracking-[0.28em] text-[#8b7964]">
              Esta análise não pôde ser realizada
            </p>

            <h2 className="mt-5 max-w-2xl font-serif text-4xl leading-tight tracking-[-0.03em] text-[#0d1b2a] sm:text-5xl">
              Parece que esta descrição está

              <span className="block italic text-[#7f8f7a]">
                fora da proposta da Lumina.
              </span>
            </h2>

            <p className="mt-6 max-w-2xl text-sm leading-7 text-[#646864] sm:text-base">
              {resultado.mensagem}
            </p>

            <div className="mt-10 border-t border-[#e0dad2] pt-8">
              <p className="max-w-xl text-sm leading-7 text-[#696d68]">
                A Lumina foi desenvolvida para
                interpretar informações sobre
                características cosméticas da pele
                facial humana.
              </p>

              <a
                href="#experiencia-analise"
                className="
                  mt-7 inline-flex
                  rounded-full
                  bg-[#0d1b2a]
                  px-7 py-3.5
                  text-sm font-medium
                  text-white
                  transition-transform
                  hover:-translate-y-0.5
                "
              >
                Editar minha descrição
              </a>
            </div>
          </div>
        </motion.div>
      </section>
    )
  }


  if (
    'status' in resultado &&
    resultado.status ===
    'informacoes_insuficientes'
  ) {
    const sugestoes = [
      'Como o seu rosto costuma se comportar ao longo do dia?',
      'Você percebe brilho mesmo quando não está praticando exercícios?',
      'Algumas regiões do rosto parecem mais secas ou mais brilhantes que outras?',
      'Algum produto costuma causar ardor, desconforto ou irritação?',
    ]

    return (
      <section
        id="resultado-analise"
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
            duration: 0.7,
            ease: 'easeOut',
          }}
        >
          <div className="rounded-[2.5rem] border border-[#ded8cf] bg-white/60 p-8 sm:p-12 lg:p-14">
            <p className="text-xs uppercase tracking-[0.28em] text-[#8b7964]">
              Precisamos de um pouco mais
            </p>

            <h2 className="mt-5 max-w-2xl font-serif text-4xl leading-tight tracking-[-0.03em] text-[#0d1b2a] sm:text-5xl">
              Ainda não conseguimos definir

              <span className="block italic text-[#7f8f7a]">
                seu perfil com segurança.
              </span>
            </h2>

            <p className="mt-6 max-w-2xl text-sm leading-7 text-[#646864] sm:text-base">
              Isso não significa que há algo errado
              com a sua descrição. Algumas
              características podem depender do
              contexto e precisamos evitar conclusões
              sem informações suficientes.
            </p>

            <div className="mt-12 border-t border-[#e0dad2] pt-9">
              <p className="text-xs uppercase tracking-[0.22em] text-[#8b7964]">
                Para complementar
              </p>

              <p className="mt-3 max-w-xl text-sm leading-7 text-[#696d68]">
                Você pode acrescentar informações como:
              </p>

              <div className="mt-7 grid gap-3 md:grid-cols-2">
                {sugestoes.map(
                  (sugestao, indice) => (
                    <motion.div
                      key={sugestao}
                      className="rounded-2xl border border-[#e3ddd4] bg-[#f7f5f1]/70 p-5"
                      initial={{
                        opacity: 0,
                        y: 12,
                      }}
                      animate={{
                        opacity: 1,
                        y: 0,
                      }}
                      transition={{
                        duration: 0.5,
                        delay:
                          0.15 +
                          indice * 0.08,
                        ease: 'easeOut',
                      }}
                    >
                      <div className="flex gap-4">
                        <span className="font-serif text-sm italic text-[#b39b7c]">
                          0{indice + 1}
                        </span>

                        <p className="text-sm leading-6 text-[#60645f]">
                          {sugestao}
                        </p>
                      </div>
                    </motion.div>
                  ),
                )}
              </div>

              <div className="mt-9 flex flex-col gap-4 sm:flex-row sm:items-center">
                <a
                  href="#experiencia-analise"
                  className="rounded-full bg-[#0d1b2a] px-7 py-3.5 text-center text-sm font-medium text-white transition-transform hover:-translate-y-0.5"
                >
                  Complementar descrição
                </a>

                <span className="text-xs text-[#8a8d87]">
                  Você pode editar o texto anterior e
                  tentar novamente.
                </span>
              </div>
            </div>
          </div>
        </motion.div>
      </section>
    )
  }

  return (
    <section
      id="resultado-analise"
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
            <p className="text-xs font-medium uppercase tracking-[0.3em] text-[#8b7964]">
              Recomendações para o seu perfil
            </p>

            <h2 className="mt-5 font-serif text-4xl leading-tight tracking-[-0.03em] text-[#0d1b2a] sm:text-5xl lg:text-6xl">
              Encontramos cuidados

              <span className="block italic text-[#7f8f7a]">
                para o seu perfil.
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
                resultado.perfil.tipo_pele
                ]
              }
            </p>

            <p className="mt-4 max-w-lg text-sm leading-7 text-[#696d68]">
              As recomendações abaixo foram
              selecionadas de acordo com as
              características deste perfil.
            </p>
          </div>
        </motion.div>

        <RecommendationsRoutine
          recomendacoes={
            resultado.recomendacoes
          }
          totalRecomendacoes={
            resultado.total_recomendacoes
          }
        />

        <motion.p
          className="mx-auto mt-20 max-w-2xl text-center text-xs leading-6 text-[#8a8d87]"
          initial={{
            opacity: 0,
          }}
          animate={{
            opacity: 1,
          }}
          transition={{
            duration: 0.8,
            delay: 0.8,
          }}
        >
          As recomendações são informativas e
          baseadas nas características compartilhadas
          e nas regras de compatibilidade do catálogo.
        </motion.p>
      </div>
    </section>
  )
}

export default AnalysisResult
