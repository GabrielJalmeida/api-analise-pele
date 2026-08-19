import {
  useEffect,
  useRef,
  useState,
} from 'react'

import type {
  ChangeEvent,
} from 'react'

import { motion } from 'motion/react'

import {
  analisarFoto,
  ErroApi,
  prepararServico,
} from '../services/api'

import type {
  RespostaAnaliseFoto,
} from '../types/analise'

interface PhotoAnalysisProps {
  onResultado: (
    resultado: RespostaAnaliseFoto,
  ) => void
}

const TAMANHO_MAXIMO =
  5 * 1024 * 1024

const LIMITE_TEXTO = 1000

const TIPOS_PERMITIDOS = [
  'image/jpeg',
  'image/png',
  'image/webp',
]

function PhotoAnalysis({
  onResultado,
}: PhotoAnalysisProps) {
  const inputRef =
    useRef<HTMLInputElement | null>(null)

  const [arquivo, setArquivo] =
    useState<File | null>(null)

  const [preview, setPreview] =
    useState<string | null>(null)

  const [
    textoComplementar,
    setTextoComplementar,
  ] = useState('')

  const [erro, setErro] =
    useState<string | null>(null)

  const [carregando, setCarregando] =
    useState(false)

  const [segundosEspera, setSegundosEspera] =
    useState(0)

  const textoPreenchido =
    textoComplementar.trim().length > 0

  const textoInvalido =
    textoPreenchido &&
    textoComplementar.trim().length < 10

  useEffect(() => {
    if (!arquivo) {
      setPreview(null)
      return
    }

    const url =
      URL.createObjectURL(arquivo)

    setPreview(url)

    return () => {
      URL.revokeObjectURL(url)
    }
  }, [arquivo])

  useEffect(() => {
    if (!carregando) {
      setSegundosEspera(0)
      return
    }

    const temporizador =
      window.setInterval(() => {
        setSegundosEspera(
          (segundos) => segundos + 1,
        )
      }, 1000)

    return () => {
      window.clearInterval(
        temporizador,
      )
    }
  }, [carregando])

  const mensagemCarregamento =
    segundosEspera < 8
      ? 'Preparando a imagem e iniciando a leitura visual.'
      : segundosEspera < 25
        ? 'A inteligência artificial está examinando apenas as características visíveis.'
        : 'A análise ainda está em andamento. Mantenha esta página aberta; algumas imagens podem levar mais tempo.'

  function selecionarArquivo(
    evento: ChangeEvent<HTMLInputElement>,
  ) {
    const arquivoSelecionado =
      evento.target.files?.[0]

    if (!arquivoSelecionado) {
      return
    }

    if (
      !TIPOS_PERMITIDOS.includes(
        arquivoSelecionado.type,
      )
    ) {
      setErro(
        'Escolha uma imagem JPG, PNG ou WEBP.',
      )

      evento.target.value = ''
      return
    }

    if (
      arquivoSelecionado.size >
      TAMANHO_MAXIMO
    ) {
      setErro(
        'A imagem não pode ultrapassar 5 MB.',
      )

      evento.target.value = ''
      return
    }

    setErro(null)
    setArquivo(arquivoSelecionado)

    // Antecipamos o despertar de hospedagens gratuitas
    // enquanto a pessoa revisa a foto escolhida.
    void prepararServico().catch(() => undefined)
  }

  function removerArquivo() {
    setArquivo(null)
    setTextoComplementar('')
    setErro(null)

    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  async function enviarAnalise() {
    if (!arquivo || textoInvalido) {
      return
    }

    try {
      setCarregando(true)
      setErro(null)

      const resposta =
        await analisarFoto(
          arquivo,
          textoComplementar,
        )

      onResultado(resposta)
    } catch (erroRecebido) {
      if (
        erroRecebido instanceof ErroApi
      ) {
        setErro(
          erroRecebido.message,
        )
        return
      }

      if (
        erroRecebido instanceof TypeError
      ) {
        setErro(
          'A conexão foi interrompida durante a análise. Sua foto continua selecionada; tente novamente.',
        )
        return
      }

      setErro(
        'Não foi possível concluir a análise da imagem.',
      )
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="mt-12">
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={selecionarArquivo}
      />

      <div className="mb-6 rounded-[1.5rem] border border-[#ddd8cf] bg-white/40 px-6 py-5">
        <p className="text-sm font-medium text-[#0d1b2a]">
          Para uma análise melhor
        </p>

        <div className="mt-4 grid gap-x-8 gap-y-3 text-xs leading-5 text-[#747872] sm:grid-cols-2">
          <div className="flex gap-2">
            <span className="text-[#879681]">
              ✓
            </span>

            <span>
              Pode ser o rosto inteiro ou uma região
              ampla, como uma bochecha.
            </span>
          </div>

          <div className="flex gap-2">
            <span className="text-[#879681]">
              ✓
            </span>

            <span>
              Mais regiões visíveis ajudam a estimar
              o tipo de pele.
            </span>
          </div>

          <div className="flex gap-2">
            <span className="text-[#879681]">
              ✓
            </span>

            <span>
              Prefira iluminação uniforme.
            </span>
          </div>

          <div className="flex gap-2">
            <span className="text-[#879681]">
              ✓
            </span>

            <span>
              Evite filtros, maquiagem intensa e
              pele molhada.
            </span>
          </div>
        </div>
      </div>

      {!preview ? (
        <motion.button
          type="button"
          onClick={() =>
            inputRef.current?.click()
          }
          className="
            group flex min-h-[280px] w-full
            flex-col items-center justify-center
            rounded-[2rem]
            border border-dashed border-[#cfc7bc]
            bg-white/50
            px-6 py-12
            text-center
            transition-colors
            hover:border-[#9aa794]
            hover:bg-white/70
          "
          whileHover={{
            y: -2,
          }}
          whileTap={{
            scale: 0.995,
          }}
        >
          <div
            className="
              flex h-14 w-14
              items-center justify-center
              rounded-full
              bg-[#a9b6a2]/20
              text-2xl
              text-[#667061]
              transition-transform
              group-hover:scale-105
            "
          >
            +
          </div>

          <p className="mt-6 font-serif text-2xl text-[#0d1b2a]">
            Escolha uma foto
          </p>

          <p className="mt-3 max-w-md text-sm leading-7 text-[#777a74]">
            Uma região facial pode ser analisada,
            mas uma foto mais ampla ajuda a estimar
            o perfil do rosto inteiro.
          </p>

          <span className="mt-6 text-xs uppercase tracking-[0.18em] text-[#9b8c79]">
            JPG · PNG · WEBP · até 5 MB
          </span>
        </motion.button>
      ) : (
        <motion.div
          className="
            overflow-hidden
            rounded-[2.25rem]
            border border-[#ded8cf]
            bg-white/60
            shadow-[0_24px_70px_rgba(13,27,42,0.06)]
          "
          initial={{
            opacity: 0,
            y: 16,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.5,
            ease: 'easeOut',
          }}
        >
          <div className="grid xl:grid-cols-[0.95fr_1.05fr]">
            <div
              className="
    relative
    min-h-[340px]
    overflow-hidden
    bg-[#e8e1d7]
    sm:min-h-[440px]
    xl:min-h-[640px]
  "
            >
              <img
                src={preview}
                alt=""
                aria-hidden="true"
                className="
      absolute inset-0
      h-full w-full
      scale-110
      object-cover
      opacity-20
      blur-2xl
    "
              />

              <div className="absolute inset-0 bg-[#f7f5f1]/25" />

              <img
                src={preview}
                alt="Pré-visualização da imagem selecionada"
                className="
      absolute inset-0
      z-10
      h-full w-full
      object-contain
      p-4
      sm:p-6
    "
              />

              <div
                className="
                  pointer-events-none
                  absolute inset-0
                  bg-gradient-to-t
                  from-[#0d1b2a]/50
                  via-transparent
                  to-transparent
                "
              />

              <div className="absolute left-6 top-6 z-20">
                <span
                  className="
                    rounded-full
                    border border-white/30
                    bg-white/80
                    px-4 py-2
                    text-[11px]
                    uppercase
                    tracking-[0.18em]
                    text-[#5f625f]
                    backdrop-blur-md
                  "
                >
                  Imagem selecionada
                </span>
              </div>

              <div className="absolute bottom-6 left-6 right-6 z-20">
                <div
                  className="
                    inline-flex max-w-full
                    items-center gap-3
                    rounded-2xl
                    border border-white/20
                    bg-[#0d1b2a]/45
                    px-4 py-3
                    text-white
                    backdrop-blur-md
                  "
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">
                      {arquivo?.name}
                    </p>

                    <p className="mt-1 text-[11px] text-white/70">
                      {arquivo
                        ? (
                          arquivo.size /
                          1024 /
                          1024
                        ).toFixed(2)
                        : '0'}{' '}
                      MB
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div
              className="
                flex flex-col
                p-7
                sm:p-10
                xl:min-h-[640px]
                xl:p-12
              "
            >
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-[#8b7964]">
                  Sua análise
                </p>

                <h3
                  className="
                    mt-4
                    max-w-xl
                    font-serif
                    text-3xl
                    leading-tight
                    tracking-[-0.03em]
                    text-[#0d1b2a]
                    sm:text-4xl
                  "
                >
                  Tudo pronto para

                  <span className="block italic text-[#7f8f7a]">
                    conhecer melhor sua pele.
                  </span>
                </h3>

                <p className="mt-5 max-w-xl text-sm leading-7 text-[#70746e]">
                  A foto já pode ser analisada. Se
                  quiser, acrescente algumas
                  informações sobre como sua pele
                  costuma se comportar ao longo do
                  dia.
                </p>

                <div className="mt-9 border-t border-[#e3ddd5] pt-8">
                  <label
                    htmlFor="descricao-foto"
                    className="text-sm font-medium text-[#0d1b2a]"
                  >
                    Quer complementar sua foto?
                  </label>

                  <p className="mt-2 max-w-xl text-xs leading-5 text-[#858982]">
                    É opcional. Essas informações
                    ajudam especialmente quando a
                    fotografia mostra somente uma
                    região do rosto.
                  </p>

                  <textarea
                    id="descricao-foto"
                    value={textoComplementar}
                    onChange={(evento) =>
                      setTextoComplementar(
                        evento.target.value,
                      )
                    }
                    maxLength={LIMITE_TEXTO}
                    disabled={carregando}
                    placeholder="Ex.: Minha testa e meu nariz ficam oleosos durante o dia, mas minhas bochechas às vezes ressecam..."
                    className="
                      mt-5
                      min-h-[140px]
                      w-full
                      resize-none
                      rounded-[1.5rem]
                      border border-[#d9d2c8]
                      bg-[#faf8f4]
                      px-5 py-4
                      text-sm
                      leading-7
                      text-[#0d1b2a]
                      outline-none
                      transition
                      placeholder:text-[#aaa69f]
                      focus:border-[#9eab98]
                      focus:bg-white
                      disabled:cursor-not-allowed
                      disabled:opacity-60
                    "
                  />

                  <div className="mt-3 flex items-center justify-between gap-4">
                    <p
                      className={`text-xs ${textoInvalido
                          ? 'text-[#9b6255]'
                          : 'text-[#989b95]'
                        }`}
                    >
                      {textoInvalido
                        ? 'Escreva pelo menos 10 caracteres ou deixe o campo vazio.'
                        : 'A descrição é opcional.'}
                    </p>

                    <span className="shrink-0 text-xs text-[#989b95]">
                      {
                        textoComplementar.length
                      }
                      /{LIMITE_TEXTO}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-auto pt-10">
                <button
                  type="button"
                  onClick={enviarAnalise}
                  disabled={
                    carregando ||
                    textoInvalido
                  }
                  className="
                    flex w-full
                    items-center
                    justify-center
                    rounded-full
                    bg-[#0d1b2a]
                    px-7 py-4
                    text-sm
                    font-medium
                    text-white
                    transition-all
                    hover:-translate-y-0.5
                    hover:bg-[#13283d]
                    disabled:cursor-not-allowed
                    disabled:translate-y-0
                    disabled:opacity-50
                  "
                >
                  {carregando
                    ? 'Analisando...'
                    : erro
                      ? 'Tentar novamente'
                    : textoPreenchido
                      ? 'Analisar foto e descrição'
                      : 'Analisar esta foto'}
                </button>

                <button
                  type="button"
                  onClick={removerArquivo}
                  disabled={carregando}
                  className="
                    mt-4 w-full
                    py-2
                    text-center
                    text-xs
                    uppercase
                    tracking-[0.18em]
                    text-[#777b75]
                    transition-colors
                    hover:text-[#0d1b2a]
                    disabled:cursor-not-allowed
                    disabled:opacity-50
                  "
                >
                  Escolher outra imagem
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {carregando && (
        <motion.div
          className="mt-6 flex items-center gap-4 rounded-2xl border border-[#d7ddd3] bg-[#eef1eb] px-5 py-5"
          initial={{
            opacity: 0,
            y: 8,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
        >
          <motion.span
            className="h-2.5 w-2.5 rounded-full bg-[#879681]"
            animate={{
              opacity: [
                0.35,
                1,
                0.35,
              ],
              scale: [
                0.9,
                1.1,
                0.9,
              ],
            }}
            transition={{
              duration: 1.2,
              repeat: Infinity,
            }}
          />

          <div>
            <p className="text-sm font-medium text-[#0d1b2a]">
              Analisando seu perfil
            </p>

            <p className="mt-1 text-xs leading-5 text-[#777b75]">
              {mensagemCarregamento}
            </p>
          </div>
        </motion.div>
      )}

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

      <div className="mt-6 flex flex-wrap gap-x-6 gap-y-2 text-xs text-[#8a8d87]">
        <span>Descrição opcional</span>
        <span>Imagem não armazenada</span>
        <span>Análise cosmética</span>
      </div>
    </div>
  )
}

export default PhotoAnalysis
