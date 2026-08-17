import { motion } from 'motion/react'

import ManualProfile from './ManualProfile'
import PhotoAnalysis from './PhotoAnalysis'
import TextAnalysis from './TextAnalysis'

import type {
  RespostaAnaliseFoto,
  RespostaAnaliseTexto,
  RespostaRecomendacoes,
  TipoAnalise,
} from '../types/analise'

interface AnalysisWorkspaceProps {
  tipoAnalise: TipoAnalise
  onVoltar: () => void

  onResultadoTexto: (
    resultado: RespostaAnaliseTexto,
  ) => void

  onResultadoFoto: (
    resultado: RespostaAnaliseFoto,
  ) => void

  onResultadoManual: (
    resultado: RespostaRecomendacoes,
  ) => void
}

const conteudo = {
  foto: {
    marcador: 'Análise visual',
    titulo: 'Vamos começar pela sua foto.',
    descricao:
      'Selecione uma imagem clara do rosto para conferir antes de iniciar a análise.',
  },

  texto: {
    marcador: 'Por descrição',
    titulo: 'Conte como você percebe sua pele.',
    descricao:
      'Descreva sua pele com suas próprias palavras para que possamos interpretar as informações.',
  },

  manual: {
    marcador: 'Sem inteligência artificial',
    titulo: 'Informe seu perfil diretamente.',
    descricao:
      'Selecione algumas características da sua pele para receber recomendações sem utilizar IA.',
  },
}

function AnalysisWorkspace({
  tipoAnalise,
  onVoltar,
  onResultadoTexto,
  onResultadoFoto,
  onResultadoManual,
}: AnalysisWorkspaceProps) {
  const experiencia =
    conteudo[tipoAnalise]

  return (
    <section
      id="experiencia-analise"
      className="bg-[#ede6dc] px-6 py-24 lg:px-10 lg:py-32"
    >
      <motion.div
        key={tipoAnalise}
        className="mx-auto max-w-4xl"
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
          ease: 'easeOut',
        }}
      >
        <button
          type="button"
          onClick={onVoltar}
          className="text-sm text-[#70736f] transition-colors hover:text-[#0d1b2a]"
        >
          ← Escolher outra opção
        </button>

        <div className="mt-12 rounded-[2.5rem] border border-white/60 bg-[#f7f5f1]/80 p-8 shadow-sm backdrop-blur-sm sm:p-12">
          <p className="text-xs uppercase tracking-[0.28em] text-[#8b7964]">
            {experiencia.marcador}
          </p>

          <h2 className="mt-5 max-w-2xl font-serif text-4xl leading-tight tracking-[-0.03em] text-[#0d1b2a] sm:text-5xl">
            {experiencia.titulo}
          </h2>

          <p className="mt-6 max-w-xl text-sm leading-7 text-[#646864] sm:text-base">
            {experiencia.descricao}
          </p>

          {tipoAnalise === 'foto' && (
            <PhotoAnalysis
              onResultado={onResultadoFoto}
            />
          )}

          {tipoAnalise === 'texto' && (
            <TextAnalysis
              onResultado={onResultadoTexto}
            />
          )}

          {tipoAnalise === 'manual' && (
            <ManualProfile
              onResultado={onResultadoManual}
            />
          )}
        </div>
      </motion.div>
    </section>
  )
}

export default AnalysisWorkspace