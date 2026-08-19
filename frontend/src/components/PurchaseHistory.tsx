import { useEffect, useState } from 'react'
import { motion } from 'motion/react'

import {
  buscarHistoricoPedidos,
  ErroApi,
  excluirHistoricoPedidos,
} from '../services/api'
import type { Pedido } from '../types/analise'


interface PurchaseHistoryProps {
  aberto: boolean
  onFechar: () => void
}


function moeda(valor: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(valor)
}


function data(valor: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'medium',
  }).format(new Date(valor))
}


function PurchaseHistory({
  aberto,
  onFechar,
}: PurchaseHistoryProps) {
  const [pedidos, setPedidos] = useState<Pedido[]>([])
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  useEffect(() => {
    if (!aberto) {
      return
    }

    setCarregando(true)
    setErro(null)

    buscarHistoricoPedidos()
      .then((resposta) => setPedidos(resposta.pedidos))
      .catch((erroRecebido) => {
        setErro(
          erroRecebido instanceof ErroApi
            ? erroRecebido.message
            : 'Não foi possível consultar o histórico.',
        )
      })
      .finally(() => setCarregando(false))
  }, [aberto])

  useEffect(() => {
    if (!aberto) {
      return
    }

    function fecharComEscape(evento: KeyboardEvent) {
      if (evento.key === 'Escape') {
        onFechar()
      }
    }

    document.addEventListener('keydown', fecharComEscape)
    return () => document.removeEventListener('keydown', fecharComEscape)
  }, [aberto, onFechar])

  async function apagar() {
    if (!window.confirm('Apagar todo o histórico salvo neste navegador?')) {
      return
    }

    try {
      await excluirHistoricoPedidos()
      setPedidos([])
      setErro(null)
    } catch (erroRecebido) {
      setErro(
        erroRecebido instanceof ErroApi
          ? erroRecebido.message
          : 'Não foi possível apagar o histórico.',
      )
    }
  }

  if (!aberto) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-[#0d1b2a]/45 backdrop-blur-sm" role="dialog" aria-modal="true" aria-label="Histórico de pedidos">
      <button
        type="button"
        className="absolute inset-0 cursor-default"
        onClick={onFechar}
        aria-label="Fechar histórico"
      />

      <motion.aside
        className="relative z-10 h-full w-full max-w-xl overflow-y-auto bg-[#f7f5f1] px-6 py-8 shadow-2xl sm:px-10"
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
      >
        <div className="flex items-start justify-between gap-6 border-b border-[#ddd6cc] pb-7">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-[#8b7964]">Seu histórico</p>
            <h2 className="mt-3 font-serif text-3xl text-[#0d1b2a]">Rituais registrados</h2>
          </div>
          <button type="button" onClick={onFechar} className="flex h-10 w-10 items-center justify-center rounded-full border border-[#d7d0c7] text-xl" aria-label="Fechar">
            ×
          </button>
        </div>

        <p className="mt-6 text-xs leading-6 text-[#777b75]">
          As seleções ficam associadas somente a este navegador e expiram automaticamente após 365 dias.
        </p>

        {carregando && (
          <p className="mt-10 text-sm text-[#696d68]">Consultando histórico…</p>
        )}

        {erro && (
          <p className="mt-7 rounded-2xl border border-[#d8b8ae] bg-[#f8ebe7] p-4 text-sm text-[#76534b]">{erro}</p>
        )}

        {!carregando && !erro && pedidos.length === 0 && (
          <div className="mt-12 rounded-[2rem] border border-[#ddd6cc] bg-white/55 p-8 text-center">
            <p className="font-serif text-2xl text-[#0d1b2a]">Nada guardado ainda.</p>
            <p className="mt-3 text-sm leading-6 text-[#777b75]">Finalize uma rotina para registrá-la aqui.</p>
          </div>
        )}

        <div className="mt-8 space-y-5">
          {pedidos.map((pedido) => (
            <article key={pedido.codigo} className="rounded-[1.75rem] border border-[#ddd6cc] bg-white/65 p-6">
              <div className="flex items-start justify-between gap-5">
                <div>
                  <p className="text-[0.65rem] uppercase tracking-[0.2em] text-[#8b7964]">{data(pedido.criado_em)}</p>
                  <h3 className="mt-2 font-serif text-xl text-[#0d1b2a]">{pedido.codigo}</h3>
                </div>
                <strong className="font-serif text-xl font-normal">{moeda(pedido.total)}</strong>
              </div>
              <div className="mt-5 space-y-3 border-t border-[#e5dfd7] pt-5">
                {pedido.itens.map((item) => (
                  <div key={`${pedido.codigo}-${item.nome_produto}`} className="flex justify-between gap-4 text-sm text-[#666b65]">
                    <span>{item.quantidade}× {item.nome_produto}</span>
                    <span>{moeda(item.subtotal)}</span>
                  </div>
                ))}
              </div>
              <p className="mt-5 text-[0.68rem] text-[#94978f]">Demonstração · nenhuma cobrança realizada</p>
            </article>
          ))}
        </div>

        {pedidos.length > 0 && (
          <button type="button" onClick={apagar} className="mt-8 text-xs text-[#875f56] underline underline-offset-4">
            Apagar meu histórico
          </button>
        )}
      </motion.aside>
    </div>
  )
}

export default PurchaseHistory
