import {
  useState,
} from 'react'

import { motion } from 'motion/react'

import {
  analisarTexto,
  ErroApi,
} from '../services/api'

import type {
  RespostaAnaliseTexto,
} from '../types/analise'

interface TextAnalysisProps {
  onResultado: (
    resultado: RespostaAnaliseTexto,
  ) => void
}

function TextAnalysis({
  onResultado,
}: TextAnalysisProps) {
  const [texto, setTexto] = useState('')
  const [carregando, setCarregando] =
    useState(false)

  const [erro, setErro] =
    useState<string | null>(null)

  const caracteresRestantes =
    1000 - texto.length

  async function enviarAnalise() {
    const textoLimpo = texto.trim()

    if (textoLimpo.length < 10) {
      setErro(
        'Conte um pouco mais sobre como você percebe sua pele.',
      )
      return
    }

    try {
      setCarregando(true)
      setErro(null)

      const resultado =
        await analisarTexto(textoLimpo)

      onResultado(resultado)
    } catch (erroRecebido) {
      if (erroRecebido instanceof ErroApi) {
        setErro(erroRecebido.message)
        return
      }

      if (erroRecebido instanceof TypeError) {
        setErro(
          'Não foi possível conectar ao serviço. Tente novamente em alguns instantes.',
        )
        return
      }

      setErro(
        'Não foi possível concluir a análise.',
      )
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="mt-12">
      <label
        htmlFor="descricao-pele"
        className="text-sm font-medium text-[#0d1b2a]"
      >
        Como você percebe sua pele?
      </label>

      <p className="mt-2 max-w-xl text-xs leading-6 text-[#858780]">
        Você pode comentar sobre sensação ao longo do dia,
        brilho, ressecamento, sensibilidade ou outras
        características que considere relevantes.
      </p>

      <textarea
        id="descricao-pele"
        value={texto}
        maxLength={1000}
        disabled={carregando}
        onChange={(evento) =>
          setTexto(evento.target.value)
        }
        placeholder="Ex.: Minha pele costuma ficar..."
        className="
          mt-5 min-h-[180px] w-full resize-none
          rounded-[1.5rem]
          border border-[#d9d2c8]
          bg-white/70
          px-5 py-4
          text-sm leading-7
          text-[#0d1b2a]
          outline-none
          transition
          placeholder:text-[#aaa69f]
          focus:border-[#8d9a87]
          focus:ring-4 focus:ring-[#a9b6a2]/15
          disabled:cursor-not-allowed
          disabled:opacity-60
        "
      />

      <div className="mt-3 flex justify-end">
        <span className="text-xs text-[#969890]">
          {caracteresRestantes} caracteres restantes
        </span>
      </div>

      {erro && (
        <motion.div
          className="mt-5 rounded-2xl border border-[#d8b8ae] bg-[#f8ebe7] px-5 py-4"
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
            {erro}
          </p>
        </motion.div>
      )}

      <button
        type="button"
        onClick={enviarAnalise}
        disabled={
          carregando ||
          texto.trim().length < 10
        }
        className="
          mt-7 rounded-full
          bg-[#0d1b2a]
          px-7 py-3.5
          text-sm font-medium
          text-white
          transition
          hover:-translate-y-0.5
          disabled:cursor-not-allowed
          disabled:translate-y-0
          disabled:opacity-40
        "
      >
        {carregando
          ? 'Analisando...'
          : 'Analisar minha descrição'}
      </button>
    </div>
  )
}

export default TextAnalysis