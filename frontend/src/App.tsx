import {
  useEffect,
  useState,
} from 'react'

import {
  motion,
  useReducedMotion,
} from 'motion/react'

import AnalysisChoice from './components/AnalysisChoice'
import AnalysisResult from './components/AnalysisResult'
import AnalysisWorkspace from './components/AnalysisWorkspace'
import Hero from './components/Hero'
import HowItWorks from './components/HowItWorks'
import PhotoResult from './components/PhotoResult'
import PurchaseHistory from './components/PurchaseHistory'

import luminaLogo from './assets/luminaLogo.png'

import type {
  RespostaAnaliseFoto,
  RespostaAnaliseTexto,
  RespostaRecomendacoes,
  TipoAnalise,
} from './types/analise'

function App() {
  const reduzirMovimento =
    useReducedMotion()

  const [tipoAnalise, setTipoAnalise] =
    useState<TipoAnalise | null>(null)

  const [historicoAberto, setHistoricoAberto] =
    useState(false)

  const [
    resultadoTexto,
    setResultadoTexto,
  ] = useState<RespostaAnaliseTexto | null>(
    null,
  )

  const [
    resultadoFoto,
    setResultadoFoto,
  ] = useState<RespostaAnaliseFoto | null>(
    null,
  )

  const [
    resultadoManual,
    setResultadoManual,
  ] = useState<RespostaRecomendacoes | null>(
    null,
  )

  useEffect(() => {
    if (!tipoAnalise) {
      return
    }

    const areaAnalise =
      document.getElementById(
        'experiencia-analise',
      )

    areaAnalise?.scrollIntoView({
      behavior: reduzirMovimento
        ? 'auto'
        : 'smooth',
      block: 'start',
    })
  }, [
    tipoAnalise,
    reduzirMovimento,
  ])

  useEffect(() => {
    if (
      !resultadoTexto &&
      !resultadoFoto &&
      !resultadoManual
    ) {
      return
    }

    const idResultado =
      resultadoFoto
        ? 'resultado-foto'
        : 'resultado-analise'

    const resultado =
      document.getElementById(
        idResultado,
      )

    resultado?.scrollIntoView({
      behavior: reduzirMovimento
        ? 'auto'
        : 'smooth',
      block: 'start',
    })
  }, [
    resultadoTexto,
    resultadoFoto,
    resultadoManual,
    reduzirMovimento,
  ])

  function selecionarTipo(
    tipo: TipoAnalise,
  ) {
    setTipoAnalise(tipo)

    setResultadoTexto(null)
    setResultadoFoto(null)
    setResultadoManual(null)
  }

  function voltarParaEscolha() {
    setTipoAnalise(null)

    setResultadoTexto(null)
    setResultadoFoto(null)
    setResultadoManual(null)
  }

  return (
    <main className="min-h-screen bg-[#f7f5f1] text-[#0d1b2a]">
      <motion.header
        className="absolute left-0 top-0 z-20 w-full"
        initial={{
          opacity: 0,
          y: reduzirMovimento
            ? 0
            : -16,
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
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-7 lg:px-10">
          <a
            href="#"
            aria-label="Lumina Skin — início"
            className="flex items-center"
          >
            <img
              src={luminaLogo}
              alt="Lumina Skin"
              className="
                h-16 w-auto object-contain
                sm:h-20
                md:h-16
                lg:h-24
              "
            />
          </a>

          <nav className="hidden items-center gap-8 text-sm text-[#5f625f] md:flex">
            <a
              href="#como-funciona"
              className="transition-colors hover:text-[#0d1b2a]"
            >
              Como funciona
            </a>

            <a
              href="#sobre"
              className="transition-colors hover:text-[#0d1b2a]"
            >
              Sobre
            </a>

            <button
              type="button"
              onClick={() => setHistoricoAberto(true)}
              className="transition-colors hover:text-[#0d1b2a]"
            >
              Meus rituais
            </button>
          </nav>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setHistoricoAberto(true)}
              className="rounded-full border border-[#cfc8be] bg-white/45 px-4 py-2.5 text-xs text-[#0d1b2a] md:hidden"
            >
              Histórico
            </button>

            <a
              href="#analise"
              className="rounded-full bg-[#0d1b2a] px-4 py-2.5 text-xs text-white transition-transform hover:-translate-y-0.5 sm:px-5 sm:text-sm"
            >
              Começar análise
            </a>
          </div>
        </div>
      </motion.header>

      <Hero
        reduzirMovimento={
          reduzirMovimento
        }
      />

      <HowItWorks />

      <section
        id="sobre"
        className="
          scroll-mt-24
          bg-[#f7f5f1]
          px-6 py-24
          lg:px-10 lg:py-32
        "
      >
        <div className="mx-auto max-w-7xl">
          <motion.div
            className="
              grid gap-12
              border-y border-[#ddd6cc]
              py-14
              lg:grid-cols-[0.8fr_1.2fr]
              lg:items-start
              lg:py-20
            "
            initial={{
              opacity: 0,
              y: reduzirMovimento
                ? 0
                : 20,
            }}
            whileInView={{
              opacity: 1,
              y: 0,
            }}
            viewport={{
              once: true,
              amount: 0.25,
            }}
            transition={{
              duration: 0.7,
              ease: 'easeOut',
            }}
          >
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-[#8b7964]">
                Sobre a Lumina
              </p>

              <h2 className="mt-5 font-serif text-4xl leading-tight tracking-[-0.03em] text-[#0d1b2a] sm:text-5xl">
                Tecnologia para orientar,

                <span className="block italic text-[#7f8f7a]">
                  não para diagnosticar.
                </span>
              </h2>
            </div>

            <div className="max-w-2xl lg:justify-self-end">
              <p className="text-base leading-8 text-[#5f645f]">
                A Lumina Skin é uma experiência de
                cuidado cosmético que ajuda a
                interpretar características da pele
                e encontrar produtos compatíveis com
                o perfil de cada pessoa.
              </p>

              <p className="mt-6 text-sm leading-7 text-[#777b75]">
                A análise pode utilizar uma fotografia,
                uma descrição sobre o comportamento da
                pele ou informações fornecidas
                diretamente por você. A tecnologia
                auxilia na interpretação; as
                recomendações são selecionadas pelas
                regras de compatibilidade do catálogo.
              </p>

              <div className="mt-10 grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl bg-white/60 px-5 py-5">
                  <p className="text-xs uppercase tracking-[0.18em] text-[#8b7964]">
                    01
                  </p>

                  <p className="mt-3 text-sm text-[#555a55]">
                    Análise cosmética
                  </p>
                </div>

                <div className="rounded-2xl bg-white/60 px-5 py-5">
                  <p className="text-xs uppercase tracking-[0.18em] text-[#8b7964]">
                    02
                  </p>

                  <p className="mt-3 text-sm text-[#555a55]">
                    Perfil personalizado
                  </p>
                </div>

                <div className="rounded-2xl bg-white/60 px-5 py-5">
                  <p className="text-xs uppercase tracking-[0.18em] text-[#8b7964]">
                    03
                  </p>

                  <p className="mt-3 text-sm text-[#555a55]">
                    Produtos compatíveis
                  </p>
                </div>
              </div>

              <p className="mt-8 text-xs leading-6 text-[#92958e]">
                A Lumina tem finalidade informativa e
                cosmética e não substitui avaliação,
                orientação ou diagnóstico
                dermatológico.
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      <AnalysisChoice
        onSelecionar={
          selecionarTipo
        }
      />

      {tipoAnalise && (
        <>
          <AnalysisWorkspace
            tipoAnalise={
              tipoAnalise
            }
            onVoltar={
              voltarParaEscolha
            }
            onResultadoFoto={
              setResultadoFoto
            }
            onResultadoTexto={
              setResultadoTexto
            }
            onResultadoManual={
              setResultadoManual
            }
          />

          {resultadoTexto && (
            <AnalysisResult
              resultado={
                resultadoTexto
              }
            />
          )}

          {resultadoFoto && (
            <PhotoResult
              resultado={
                resultadoFoto
              }
            />
          )}

          {resultadoManual && (
            <AnalysisResult
              resultado={
                resultadoManual
              }
            />
          )}
        </>
      )}

      <PurchaseHistory
        aberto={historicoAberto}
        onFechar={() => setHistoricoAberto(false)}
      />
    </main>
  )
}

export default App
