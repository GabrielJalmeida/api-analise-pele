import { useEffect, useMemo, useState } from 'react'
import { motion } from 'motion/react'

import RoutineOrder from './RoutineOrder'
import type {
  CategoriaProduto,
  ProdutoRecomendado,
  RecomendacoesPorCategoria,
} from '../types/analise'


interface RecommendationsRoutineProps {
  recomendacoes: RecomendacoesPorCategoria
  totalRecomendacoes: number
}

interface ConfiguracaoCategoria {
  passo: string
  titulo: string
  descricao: string
  contexto: string
}

const API_URL = (
  import.meta.env.VITE_API_URL
  ?? 'http://127.0.0.1:8000'
).replace(/\/$/, '')

const configuracoesCategorias: Record<CategoriaProduto, ConfiguracaoCategoria> = {
  limpeza: {
    passo: '01',
    titulo: 'Limpeza',
    descricao: 'O gesto que prepara a pele para receber os próximos cuidados.',
    contexto: 'para começar',
  },
  serum: {
    passo: '02',
    titulo: 'Tratamento',
    descricao: 'Uma fórmula concentrada escolhida para as características do perfil.',
    contexto: 'para tratar',
  },
  hidratante: {
    passo: '03',
    titulo: 'Hidratação',
    descricao: 'Conforto e equilíbrio para acompanhar a rotina ao longo do dia.',
    contexto: 'para equilibrar',
  },
  protetor_solar: {
    passo: '04',
    titulo: 'Proteção',
    descricao: 'A etapa diária que encerra e protege o ritual da manhã.',
    contexto: 'para proteger',
  },
  outros: {
    passo: '05',
    titulo: 'Complemento',
    descricao: 'Um cuidado adicional para usar quando fizer sentido na sua rotina.',
    contexto: 'para complementar',
  },
}

const ordemCategorias: CategoriaProduto[] = [
  'limpeza',
  'serum',
  'hidratante',
  'protetor_solar',
  'outros',
]


function urlImagem(imagemUrl: string): string | null {
  if (!imagemUrl.trim()) {
    return null
  }

  if (/^https?:\/\//.test(imagemUrl)) {
    return imagemUrl
  }

  return `${API_URL}${imagemUrl}`
}


function moeda(preco: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(preco)
}


function traduzirMotivo(motivo: string): string {
  const motivos: Record<string, string> = {
    'Compatível com o tipo de pele identificado': 'Compatível com o seu perfil',
    'Indicado para pele com espinhas': 'Considera as características informadas',
    'Indicado para diferentes tipos de pele': 'Uma opção versátil para diferentes perfis',
    'Adequado para pele sensível': 'Compatível com cuidados mais delicados',
  }

  return motivos[motivo] ?? motivo
}


function ImagemProduto({
  produto,
  compacta = false,
}: {
  produto: ProdutoRecomendado
  compacta?: boolean
}) {
  const imagem = urlImagem(produto.imagem_url)

  if (imagem) {
    return (
      <img
        src={imagem}
        alt={produto.nome}
        loading="lazy"
        decoding="async"
        className="h-full w-full object-contain"
      />
    )
  }

  return (
    <div
      className={`flex h-full w-full flex-col items-center justify-center bg-[radial-gradient(circle_at_30%_25%,#f8f5ee_0,#e8e8df_52%,#d9e0d4_100%)] text-center ${compacta ? 'p-2' : 'p-8'}`}
      role="img"
      aria-label={`Produto ${produto.nome} sem imagem cadastrada`}
    >
      <span className={`${compacta ? 'text-2xl' : 'text-6xl'} font-serif italic text-[#879681]`}>
        {produto.nome.charAt(0).toUpperCase()}
      </span>
      {!compacta && (
        <span className="mt-4 text-[0.62rem] uppercase tracking-[0.22em] text-[#8a8d87]">
          Imagem não cadastrada
        </span>
      )}
    </div>
  )
}


function DetalhesProduto({
  produto,
}: {
  produto: ProdutoRecomendado
}) {
  return (
    <details className="group/detalhes mt-7 border-t border-[#dfd8cf] pt-5">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-sm font-medium text-[#0d1b2a] [&::-webkit-details-marker]:hidden">
        <span>Entenda esta escolha</span>
        <span className="flex h-8 w-8 items-center justify-center rounded-full border border-[#d8d1c8] text-lg font-light text-[#7f8f7a] transition-transform group-open/detalhes:rotate-45">
          +
        </span>
      </summary>

      <div className="mt-5 grid gap-5 text-xs leading-6 text-[#696d68] sm:grid-cols-2">
        <div>
          <p className="uppercase tracking-[0.18em] text-[#9b8061]">Ativos</p>
          <p className="mt-2">
            {produto.ativos_principais || 'Ativos principais não informados no catálogo.'}
          </p>
        </div>

        <div>
          <p className="uppercase tracking-[0.18em] text-[#9b8061]">Compatibilidade</p>
          {produto.motivos_compatibilidade.length > 0 ? (
            <ul className="mt-2 space-y-1.5">
              {produto.motivos_compatibilidade.map((motivo) => (
                <li key={`${produto.id}-${motivo}`}>
                  {traduzirMotivo(motivo)}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2">Selecionado pelas regras do perfil informado.</p>
          )}
        </div>
      </div>
    </details>
  )
}


function ProdutoDaEtapa({
  produto,
  configuracao,
}: {
  produto: ProdutoRecomendado
  configuracao: ConfiguracaoCategoria
}) {
  const descricao = produto.descricao_curta
    || 'O catálogo ainda não possui uma descrição editorial para este item. A compatibilidade foi calculada a partir dos dados disponíveis.'

  return (
    <article className="group overflow-hidden rounded-[2.5rem] border border-[#dcd5cc] bg-[#fbfaf7] shadow-[0_28px_90px_rgba(31,42,35,0.07)] lg:grid lg:grid-cols-[1.02fr_0.98fr]">
      <div className="relative flex min-h-[22rem] items-center justify-center overflow-hidden bg-[#efede7] p-6 sm:min-h-[30rem] sm:p-10">
        <div className="absolute left-6 top-6 z-10 rounded-full border border-white/60 bg-white/75 px-4 py-2 text-[0.64rem] uppercase tracking-[0.2em] text-[#65705f] backdrop-blur-sm">
          Escolha {configuracao.contexto}
        </div>
        <div className="h-[19rem] w-full sm:h-[27rem]">
          <ImagemProduto produto={produto} />
        </div>
      </div>

      <div className="flex flex-col justify-center p-7 sm:p-10 lg:p-12">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-[0.68rem] uppercase tracking-[0.2em] text-[#9b8061]">
          <span>{produto.marca || 'Marca não informada'}</span>
          {produto.conteudo && (
            <span className="normal-case tracking-normal text-[#92958e]">{produto.conteudo}</span>
          )}
        </div>

        <h4 className="mt-6 max-w-xl font-serif text-3xl leading-[1.08] tracking-[-0.025em] text-[#0d1b2a] sm:text-5xl">
          {produto.nome}
        </h4>
        <p className="mt-6 max-w-xl text-sm leading-7 text-[#696d68]">
          {descricao}
        </p>

        <div className="mt-9 flex flex-wrap items-end justify-between gap-5">
          <div>
            <p className="text-[0.64rem] uppercase tracking-[0.19em] text-[#92958e]">Valor do catálogo</p>
            <p className="mt-2 font-serif text-3xl text-[#0d1b2a]">{moeda(produto.preco)}</p>
          </div>
          <p className="flex items-center gap-2 text-xs text-[#687265]">
            <span className="h-2 w-2 rounded-full bg-[#9ead97]" />
            Selecionado para o seu perfil
          </p>
        </div>

        <DetalhesProduto produto={produto} />
      </div>
    </article>
  )
}


function RecommendationsRoutine({
  recomendacoes,
  totalRecomendacoes,
}: RecommendationsRoutineProps) {
  const categorias = useMemo(
    () => ordemCategorias.filter(
      (categoria) => Boolean(recomendacoes[categoria]?.length),
    ),
    [recomendacoes],
  )
  const [selecoes, setSelecoes] = useState<Partial<Record<CategoriaProduto, number>>>({})

  useEffect(() => {
    setSelecoes((atuais) => {
      const proximas = { ...atuais }

      for (const categoria of categorias) {
        const produtos = recomendacoes[categoria] ?? []
        const aindaExiste = produtos.some(
          (produto) => produto.id === proximas[categoria],
        )

        if (!aindaExiste && produtos[0]) {
          proximas[categoria] = produtos[0].id
        }
      }

      return proximas
    })
  }, [categorias, recomendacoes])

  const escolhidos = useMemo(
    () => categorias.flatMap((categoria) => {
      const produtos = recomendacoes[categoria] ?? []
      const escolhido = produtos.find(
        (produto) => produto.id === selecoes[categoria],
      ) ?? produtos[0]

      return escolhido ? [escolhido] : []
    }),
    [categorias, recomendacoes, selecoes],
  )

  if (categorias.length === 0) {
    return (
      <div className="mt-14 rounded-[2rem] border border-[#ded8cf] bg-white/55 p-8 text-center sm:p-12">
        <p className="font-serif text-3xl text-[#0d1b2a]">Nenhum produto disponível agora.</p>
        <p className="mx-auto mt-4 max-w-xl text-sm leading-7 text-[#70746e]">
          O perfil foi concluído, mas não há itens ativos, em estoque e compatíveis neste catálogo.
        </p>
      </div>
    )
  }

  return (
    <div className="mt-12">
      <motion.div
        className="grid gap-7 border-b border-[#ddd6cc] pb-10 lg:grid-cols-[1fr_auto] lg:items-end"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-[#8b7964]">Seu ritual</p>
          <h3 className="mt-3 max-w-3xl font-serif text-3xl leading-tight text-[#0d1b2a] sm:text-5xl">
            Não um catálogo. Uma sequência
            <span className="block italic text-[#7f8f7a]">pensada etapa por etapa.</span>
          </h3>
        </div>
        <p className="max-w-sm text-xs leading-6 text-[#858981] lg:text-right">
          Selecionamos uma opção principal em cada etapa. Você pode trocar por uma alternativa antes de guardar a rotina.
        </p>
      </motion.div>

      <div className="mt-16 space-y-24 lg:space-y-32">
        {categorias.map((categoria, indice) => {
          const produtos = recomendacoes[categoria] ?? []
          const selecionado = produtos.find(
            (produto) => produto.id === selecoes[categoria],
          ) ?? produtos[0]
          const alternativas = produtos.filter(
            (produto) => produto.id !== selecionado.id,
          )
          const configuracao = configuracoesCategorias[categoria]

          return (
            <motion.section
              key={categoria}
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.65, delay: 0.2 + indice * 0.07 }}
            >
              <div className="mb-8 grid gap-4 sm:grid-cols-[auto_1fr] sm:items-start">
                <span className="font-serif text-lg italic text-[#a28b6f]">{configuracao.passo}</span>
                <div className="sm:flex sm:items-end sm:justify-between sm:gap-8">
                  <div>
                    <h4 className="font-serif text-3xl text-[#0d1b2a] sm:text-4xl">{configuracao.titulo}</h4>
                    <p className="mt-2 max-w-xl text-sm leading-6 text-[#747872]">{configuracao.descricao}</p>
                  </div>
                  <span className="mt-3 block text-xs text-[#92958e] sm:mt-0">
                    Etapa {indice + 1} de {categorias.length}
                  </span>
                </div>
              </div>

              <ProdutoDaEtapa produto={selecionado} configuracao={configuracao} />

              {alternativas.length > 0 && (
                <div className="mt-7 rounded-[1.75rem] border border-[#ded8cf] bg-white/35 p-5 sm:p-7">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                    <div>
                      <p className="text-xs uppercase tracking-[0.2em] text-[#8b7964]">Outras possibilidades</p>
                      <p className="mt-2 text-sm text-[#747872]">Troque a escolha desta etapa sem alterar o restante da rotina.</p>
                    </div>
                    <span className="text-xs text-[#92958e]">{alternativas.length} {alternativas.length === 1 ? 'alternativa' : 'alternativas'}</span>
                  </div>

                  <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                    {alternativas.map((produto) => (
                      <button
                        key={produto.id}
                        type="button"
                        onClick={() => setSelecoes((atuais) => ({
                          ...atuais,
                          [categoria]: produto.id,
                        }))}
                        className="group flex min-w-0 items-center gap-4 rounded-2xl border border-[#e0dad2] bg-[#fbfaf7] p-3 text-left transition hover:-translate-y-0.5 hover:border-[#acb8a7] hover:shadow-[0_12px_35px_rgba(31,42,35,0.07)]"
                      >
                        <div className="h-20 w-20 shrink-0 overflow-hidden rounded-xl bg-[#efede7]">
                          <ImagemProduto produto={produto} compacta />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium text-[#0d1b2a]">{produto.nome}</p>
                          <p className="mt-1 text-xs text-[#8a8d87]">{produto.marca || 'Marca não informada'}</p>
                          <p className="mt-2 text-sm text-[#0d1b2a]">{moeda(produto.preco)}</p>
                        </div>
                        <span className="mr-1 text-lg text-[#879681] transition-transform group-hover:translate-x-0.5">→</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </motion.section>
          )
        })}
      </div>

      <div className="mt-16 rounded-[1.75rem] bg-[#ecefe9] px-6 py-5 text-xs leading-6 text-[#697066] sm:flex sm:items-center sm:justify-between sm:gap-8">
        <span>{escolhidos.length} etapas compõem sua seleção atual.</span>
        <span>{totalRecomendacoes} produtos compatíveis foram considerados no total.</span>
      </div>

      <RoutineOrder produtos={escolhidos} />
    </div>
  )
}

export default RecommendationsRoutine
