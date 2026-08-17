import { motion } from 'motion/react'

import type {
  TipoAnalise,
} from '../types/analise'

interface AnalysisChoiceProps {
  onSelecionar: (
    tipo: TipoAnalise,
  ) => void
}

const opcoes: {
  id: TipoAnalise
  numero: string
  titulo: string
  destaque: string
  descricao: string
  detalhe: string
}[] = [
  {
    id: 'foto',
    numero: '01',
    titulo: 'Enviar uma foto',
    destaque: 'Análise visual',
    descricao:
      'Compartilhe uma imagem da sua pele e deixe a tecnologia identificar características relevantes para o seu perfil.',
    detalhe: 'JPG, PNG ou WEBP',
  },
  {
    id: 'texto',
    numero: '02',
    titulo: 'Descrever minha pele',
    destaque: 'Por descrição',
    descricao:
      'Conte com suas próprias palavras como percebe sua pele e nós interpretamos essas informações.',
    detalhe: 'Sem necessidade de foto',
  },
  {
    id: 'manual',
    numero: '03',
    titulo: 'Continuar sem IA',
    destaque: 'Perfil informado',
    descricao:
      'Se você já conhece seu perfil, informe algumas características e vá diretamente para as recomendações.',
    detalhe: 'IA opcional',
  },
]

function AnalysisChoice({
  onSelecionar,
}: AnalysisChoiceProps) {
  return (
    <section
      id="analise"
      className="
        bg-[#f7f5f1]
        px-6 pb-28 pt-10
        sm:pb-32
        lg:px-10 lg:pb-40
      "
    >
      <div className="mx-auto max-w-7xl">
        <motion.div
          className="mx-auto max-w-3xl text-center"
          initial={{
            opacity: 0,
            y: 24,
          }}
          whileInView={{
            opacity: 1,
            y: 0,
          }}
          viewport={{
            once: true,
            amount: 0.4,
          }}
          transition={{
            duration: 0.7,
            ease: 'easeOut',
          }}
        >
          <p className="text-xs font-medium uppercase tracking-[0.3em] text-[#8b7964]">
            Sua análise
          </p>

          <h2 className="mt-5 font-serif text-4xl leading-tight tracking-[-0.03em] text-[#0d1b2a] sm:text-5xl lg:text-6xl">
            Escolha como deseja

            <span className="block italic text-[#7f8f7a]">
              começar.
            </span>
          </h2>

          <p className="mx-auto mt-6 max-w-xl text-sm leading-7 text-[#686b67] sm:text-base">
            Não existe uma única forma de usar
            a Lumina. Escolha a experiência que
            fizer mais sentido para você.
          </p>
        </motion.div>

        <div className="mt-16 grid items-stretch gap-5 lg:grid-cols-3">
          {opcoes.map(
            (
              opcao,
              indice,
            ) => (
              <motion.button
                key={opcao.id}
                type="button"
                onClick={() =>
                  onSelecionar(
                    opcao.id,
                  )
                }
                className="
                  group relative
                  flex h-full
                  min-h-[390px]
                  flex-col
                  overflow-hidden
                  rounded-[2rem]
                  border border-[#ded8cf]
                  bg-[#fbfaf7]
                  p-7
                  text-left
                  transition-colors
                  hover:border-[#b8afa2]
                  sm:p-8
                  lg:min-h-[420px]
                  xl:min-h-[400px]
                "
                initial={{
                  opacity: 0,
                  y: 30,
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
                  duration: 0.65,
                  delay:
                    indice * 0.1,
                  ease: 'easeOut',
                }}
                whileHover={{
                  y: -5,
                }}
                whileTap={{
                  scale: 0.99,
                }}
              >
                <div className="relative z-10 flex items-start justify-between">
                  <span className="font-serif text-2xl italic text-[#b39b7c]">
                    {opcao.numero}
                  </span>

                  <span
                    className="
                      flex h-10 w-10
                      shrink-0
                      items-center justify-center
                      rounded-full
                      border border-[#ded8cf]
                      text-lg
                      text-[#0d1b2a]
                      transition-all
                      group-hover:border-[#0d1b2a]
                      group-hover:bg-[#0d1b2a]
                      group-hover:text-white
                    "
                  >
                    →
                  </span>
                </div>

                <div className="relative z-10 mt-12">
                  <p className="text-xs uppercase tracking-[0.22em] text-[#8b7964]">
                    {opcao.destaque}
                  </p>

                  <h3
                    className="
                      mt-3
                      font-serif
                      text-3xl
                      leading-tight
                      tracking-[-0.02em]
                      text-[#0d1b2a]
                      lg:text-[1.7rem]
                      xl:text-3xl
                    "
                  >
                    {opcao.titulo}
                  </h3>

                  <p className="mt-5 max-w-sm text-sm leading-7 text-[#646864]">
                    {opcao.descricao}
                  </p>
                </div>

                <div
                  className="
                    relative z-10
                    mt-auto
                    pt-8
                  "
                >
                  <div className="border-t border-[#e4dfd8] pt-5">
                    <span className="text-xs text-[#8a8d87]">
                      {opcao.detalhe}
                    </span>
                  </div>
                </div>

                <div
                  className="
                    pointer-events-none
                    absolute
                    -bottom-20 -right-20
                    h-40 w-40
                    rounded-full
                    bg-[#a9b6a2]/0
                    blur-2xl
                    transition-all
                    duration-500
                    group-hover:bg-[#a9b6a2]/20
                  "
                />
              </motion.button>
            ),
          )}
        </div>

        <p className="mx-auto mt-10 max-w-xl text-center text-xs leading-6 text-[#8a8d87]">
          A análise tem finalidade informativa e
          cosmética. Ela não substitui avaliação
          dermatológica.
        </p>
      </div>
    </section>
  )
}

export default AnalysisChoice