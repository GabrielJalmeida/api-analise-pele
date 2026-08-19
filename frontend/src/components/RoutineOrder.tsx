import { useMemo, useState } from 'react'
import { motion } from 'motion/react'

import { ErroApi, registrarPedido } from '../services/api'
import type {
  Pedido,
  ProdutoRecomendado,
} from '../types/analise'


interface RoutineOrderProps {
  produtos: ProdutoRecomendado[]
}


function formatarPreco(preco: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(preco)
}


function RoutineOrder({
  produtos,
}: RoutineOrderProps) {
  const [aberto, setAberto] = useState(false)
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [consentimento, setConsentimento] =
    useState(false)
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [pedido, setPedido] = useState<Pedido | null>(null)

  const total = useMemo(
    () => produtos.reduce(
      (soma, produto) => soma + produto.preco,
      0,
    ),
    [produtos],
  )

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault()

    if (!consentimento) {
      setErro('Confirme a retenção do histórico para registrar a seleção.')
      return
    }

    try {
      setEnviando(true)
      setErro(null)

      const resposta = await registrarPedido(
        nome.trim(),
        email.trim(),
        produtos.map((produto) => produto.id),
        consentimento,
      )

      setPedido(resposta.pedido)
    } catch (erroRecebido) {
      if (erroRecebido instanceof ErroApi) {
        setErro(erroRecebido.message)
      } else {
        setErro('Não foi possível registrar sua seleção. Tente novamente.')
      }
    } finally {
      setEnviando(false)
    }
  }

  if (pedido) {
    return (
      <motion.div
        className="mt-12 rounded-[2rem] border border-[#cad5c5] bg-[#edf2e9] p-7 sm:p-10"
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <p className="text-xs uppercase tracking-[0.25em] text-[#65745f]">
          Seleção registrada
        </p>
        <h4 className="mt-4 font-serif text-3xl text-[#0d1b2a]">
          Seu ritual ficou guardado.
        </h4>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-[#626b60]">
          Código {pedido.codigo}. Esta é uma demonstração: nenhuma cobrança ou compra real foi realizada.
        </p>
        <p className="mt-5 text-sm font-medium text-[#0d1b2a]">
          Total demonstrativo: {formatarPreco(pedido.total)}
        </p>
      </motion.div>
    )
  }

  return (
    <section className="mt-20 border-t border-[#dcd5cc] pt-12">
      <div className="grid gap-10 lg:grid-cols-[1fr_0.8fr] lg:items-start">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-[#8b7964]">
            Sua seleção completa
          </p>
          <h3 className="mt-4 max-w-xl font-serif text-4xl leading-tight text-[#0d1b2a] sm:text-5xl">
            Guarde este ritual
            <span className="block italic text-[#7f8f7a]">para consultar depois.</span>
          </h3>
          <p className="mt-6 max-w-xl text-sm leading-7 text-[#696d68]">
            O registro abaixo simula um pedido para demonstrar a integração. Não há checkout, pagamento ou coleta de dados de cartão.
          </p>
        </div>

        <div className="rounded-[2rem] border border-[#ddd6cc] bg-white/55 p-6 sm:p-8">
          <div className="space-y-4">
            {produtos.map((produto) => (
              <div
                key={produto.id}
                className="flex items-start justify-between gap-5 border-b border-[#e7e1d9] pb-4 last:border-0 last:pb-0"
              >
                <div>
                  <p className="text-sm font-medium text-[#0d1b2a]">
                    {produto.nome}
                  </p>
                  <p className="mt-1 text-xs text-[#858981]">
                    {produto.marca || 'Marca não informada'}
                  </p>
                </div>
                <span className="shrink-0 text-sm text-[#0d1b2a]">
                  {formatarPreco(produto.preco)}
                </span>
              </div>
            ))}
          </div>

          <div className="mt-6 flex items-center justify-between border-t border-[#d7d0c7] pt-5">
            <span className="text-sm text-[#696d68]">Total</span>
            <strong className="font-serif text-2xl font-normal text-[#0d1b2a]">
              {formatarPreco(total)}
            </strong>
          </div>

          {!aberto ? (
            <button
              type="button"
              onClick={() => setAberto(true)}
              className="mt-7 w-full rounded-full bg-[#0d1b2a] px-6 py-4 text-sm font-medium text-white transition-transform hover:-translate-y-0.5"
            >
              Registrar esta seleção
            </button>
          ) : (
            <form onSubmit={enviar} className="mt-8 space-y-5 border-t border-[#e3ddd4] pt-7">
              <div>
                <label htmlFor="pedido-nome" className="text-xs uppercase tracking-[0.16em] text-[#7b6a57]">
                  Nome
                </label>
                <input
                  id="pedido-nome"
                  value={nome}
                  onChange={(evento) => setNome(evento.target.value)}
                  minLength={2}
                  maxLength={100}
                  required
                  autoComplete="name"
                  className="mt-2 w-full rounded-2xl border border-[#d7d0c7] bg-[#fbfaf7] px-4 py-3 text-sm outline-none transition focus:border-[#8f9f89]"
                />
              </div>

              <div>
                <label htmlFor="pedido-email" className="text-xs uppercase tracking-[0.16em] text-[#7b6a57]">
                  E-mail
                </label>
                <input
                  id="pedido-email"
                  type="email"
                  value={email}
                  onChange={(evento) => setEmail(evento.target.value)}
                  maxLength={254}
                  required
                  autoComplete="email"
                  className="mt-2 w-full rounded-2xl border border-[#d7d0c7] bg-[#fbfaf7] px-4 py-3 text-sm outline-none transition focus:border-[#8f9f89]"
                />
              </div>

              <label className="flex cursor-pointer items-start gap-3 text-xs leading-6 text-[#696d68]">
                <input
                  type="checkbox"
                  checked={consentimento}
                  onChange={(evento) => setConsentimento(evento.target.checked)}
                  className="mt-1 h-4 w-4 accent-[#0d1b2a]"
                />
                <span>
                  Concordo que nome, e-mail e esta seleção sejam mantidos por até 1 ano. Posso apagar o histórico a qualquer momento neste navegador.
                </span>
              </label>

              {erro && (
                <p className="rounded-2xl border border-[#d8b8ae] bg-[#f8ebe7] px-4 py-3 text-xs leading-5 text-[#76534b]">
                  {erro}
                </p>
              )}

              <button
                type="submit"
                disabled={enviando}
                className="w-full rounded-full bg-[#0d1b2a] px-6 py-4 text-sm font-medium text-white disabled:cursor-wait disabled:opacity-60"
              >
                {enviando ? 'Registrando…' : 'Confirmar registro demonstrativo'}
              </button>
            </form>
          )}
        </div>
      </div>
    </section>
  )
}

export default RoutineOrder
