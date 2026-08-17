import {
  useState,
} from 'react'

import { motion } from 'motion/react'

import {
  buscarRecomendacoes,
  ErroApi,
} from '../services/api'

import type {
  RespostaRecomendacoes,
  TipoPele,
} from '../types/analise'

interface ManualProfileProps {
  onResultado: (
    resultado: RespostaRecomendacoes,
  ) => void
}

const tiposPele: {
  valor: TipoPele
  titulo: string
  descricao: string
}[] = [
  {
    valor: 'oleosa',
    titulo: 'Oleosa',
    descricao:
      'Costuma apresentar oleosidade ao longo do dia.',
  },
  {
    valor: 'seca',
    titulo: 'Seca',
    descricao:
      'Costuma apresentar ressecamento ou sensação de repuxamento.',
  },
  {
    valor: 'mista',
    titulo: 'Mista',
    descricao:
      'Regiões diferentes do rosto apresentam comportamentos distintos.',
  },
  {
    valor: 'normal',
    titulo: 'Normal',
    descricao:
      'Não apresenta tendência marcante à oleosidade ou ao ressecamento.',
  },
]

function ManualProfile({
  onResultado,
}: ManualProfileProps) {
  const [
    tipoPele,
    setTipoPele,
  ] = useState<TipoPele | null>(null)

  const [
    sensivel,
    setSensivel,
  ] = useState<boolean | null>(null)

  const [
    temEspinha,
    setTemEspinha,
  ] = useState<boolean | null>(null)

  const [
    carregando,
    setCarregando,
  ] = useState(false)

  const [
    erro,
    setErro,
  ] = useState<string | null>(null)

  async function enviarPerfil() {
    if (!tipoPele) {
      setErro(
        'Selecione o tipo de pele para continuar.',
      )
      return
    }

    try {
      setCarregando(true)
      setErro(null)

      const resultado =
        await buscarRecomendacoes({
          tipo_pele: tipoPele,
          sensivel,
          tem_espinha: temEspinha,
        })

      onResultado(resultado)
    } catch (erroRecebido) {
      if (
        erroRecebido instanceof ErroApi
      ) {
        setErro(erroRecebido.message)
        return
      }

      if (
        erroRecebido instanceof TypeError
      ) {
        setErro(
          'Não foi possível conectar ao serviço.',
        )
        return
      }

      setErro(
        'Não foi possível buscar recomendações.',
      )
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="mt-12">
      <div>
        <p className="text-sm font-medium text-[#0d1b2a]">
          Como você considera seu tipo de pele?
        </p>

        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          {tiposPele.map((tipo) => {
            const selecionado =
              tipoPele === tipo.valor

            return (
              <button
                key={tipo.valor}
                type="button"
                onClick={() =>
                  setTipoPele(tipo.valor)
                }
                className={`
                  rounded-[1.5rem]
                  border p-5
                  text-left
                  transition
                  ${
                    selecionado
                      ? 'border-[#879681] bg-[#a9b6a2]/15'
                      : 'border-[#ddd6cc] bg-white/50 hover:border-[#aaa397]'
                  }
                `}
              >
                <p className="font-serif text-xl text-[#0d1b2a]">
                  {tipo.titulo}
                </p>

                <p className="mt-2 text-xs leading-6 text-[#747872]">
                  {tipo.descricao}
                </p>
              </button>
            )
          })}
        </div>
      </div>

      <div className="mt-10 border-t border-[#ddd5ca] pt-9">
        <p className="text-sm font-medium text-[#0d1b2a]">
          Sua pele costuma reagir com facilidade a produtos?
        </p>

        <div className="mt-4 flex flex-wrap gap-3">
          {[
            {
              valor: true,
              texto: 'Sim',
            },
            {
              valor: false,
              texto: 'Não',
            },
            {
              valor: null,
              texto: 'Não sei',
            },
          ].map((opcao) => (
            <button
              key={opcao.texto}
              type="button"
              onClick={() =>
                setSensivel(opcao.valor)
              }
              className={`
                rounded-full border
                px-5 py-2.5
                text-sm transition
                ${
                  sensivel === opcao.valor
                    ? 'border-[#879681] bg-[#a9b6a2]/20 text-[#0d1b2a]'
                    : 'border-[#d9d2c8] text-[#6f736d]'
                }
              `}
            >
              {opcao.texto}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-9">
        <p className="text-sm font-medium text-[#0d1b2a]">
          Você costuma ter espinhas?
        </p>

        <div className="mt-4 flex flex-wrap gap-3">
          {[
            {
              valor: true,
              texto: 'Sim',
            },
            {
              valor: false,
              texto: 'Não',
            },
            {
              valor: null,
              texto: 'Não sei',
            },
          ].map((opcao) => (
            <button
              key={opcao.texto}
              type="button"
              onClick={() =>
                setTemEspinha(opcao.valor)
              }
              className={`
                rounded-full border
                px-5 py-2.5
                text-sm transition
                ${
                  temEspinha === opcao.valor
                    ? 'border-[#879681] bg-[#a9b6a2]/20 text-[#0d1b2a]'
                    : 'border-[#d9d2c8] text-[#6f736d]'
                }
              `}
            >
              {opcao.texto}
            </button>
          ))}
        </div>
      </div>

      {erro && (
        <motion.div
          className="mt-7 rounded-2xl border border-[#d8b8ae] bg-[#f8ebe7] px-5 py-4"
          initial={{
            opacity: 0,
            y: 8,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
        >
          <p className="text-sm text-[#76534b]">
            {erro}
          </p>
        </motion.div>
      )}

      <button
        type="button"
        disabled={
          carregando ||
          !tipoPele
        }
        onClick={enviarPerfil}
        className="
          mt-9 rounded-full
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
          ? 'Buscando cuidados...'
          : 'Ver minhas recomendações'}
      </button>

      <p className="mt-5 text-xs leading-6 text-[#8a8d87]">
        Este caminho não utiliza inteligência
        artificial. As recomendações são calculadas
        diretamente a partir das características que
        você informar.
      </p>
    </div>
  )
}

export default ManualProfile