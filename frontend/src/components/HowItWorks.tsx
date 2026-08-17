import { motion } from 'motion/react'

const etapas = [
  {
    numero: '01',
    titulo: 'Compartilhe',
    descricao:
      'Envie uma foto, descreva sua pele ou continue sem inteligência artificial.',
  },
  {
    numero: '02',
    titulo: 'Nós interpretamos',
    descricao:
      'Suas informações são transformadas em um perfil estruturado para orientar a análise.',
  },
  {
    numero: '03',
    titulo: 'Descubra seus cuidados',
    descricao:
      'O sistema encontra produtos do catálogo compatíveis com o seu perfil.',
  },
]

function HowItWorks() {
  return (
    <section
      id="como-funciona"
      className="bg-[#f7f5f1] px-6 py-24 sm:py-28 lg:px-10 lg:py-32"
    >
      <motion.div
        className="mx-auto max-w-7xl overflow-hidden rounded-[2.5rem] bg-[#0d1b2a] px-6 py-16 text-[#f7f5f1] sm:px-10 lg:px-14 lg:py-20"
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
          amount: 0.2,
        }}
        transition={{
          duration: 0.8,
          ease: 'easeOut',
        }}
      >
        <div className="grid gap-10 border-b border-white/15 pb-12 lg:grid-cols-[0.8fr_1.2fr] lg:items-end">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[#dccbb4]">
              Como funciona
            </p>

            <h2 className="mt-5 max-w-lg font-serif text-4xl leading-tight tracking-[-0.03em] sm:text-5xl">
              Simples para você.
              <span className="block italic text-[#a9b6a2]">
                Inteligente por trás.
              </span>
            </h2>
          </div>

          <p className="max-w-xl text-sm leading-7 text-white/65 sm:text-base lg:justify-self-end">
            Você não precisa conhecer termos técnicos ou descobrir
            sozinho quais produtos procurar. A experiência começa
            pelas informações que você deseja compartilhar.
          </p>
        </div>

        <div className="grid lg:grid-cols-3">
          {etapas.map((etapa, indice) => (
            <motion.article
              key={etapa.numero}
              className="
                border-b border-white/15 py-10
                lg:border-b-0 lg:border-r lg:px-8 lg:py-14
                first:lg:pl-0
                last:border-b-0 last:lg:border-r-0 last:lg:pr-0
              "
              initial={{
                opacity: 0,
                y: 20,
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
                duration: 0.6,
                delay: indice * 0.12,
                ease: 'easeOut',
              }}
            >
              <span className="font-serif text-3xl italic text-[#dccbb4]">
                {etapa.numero}
              </span>

              <h3 className="mt-8 text-xl font-medium">
                {etapa.titulo}
              </h3>

              <p className="mt-4 max-w-sm text-sm leading-7 text-white/60">
                {etapa.descricao}
              </p>
            </motion.article>
          ))}
        </div>

        <div className="flex flex-col gap-4 border-t border-white/15 pt-8 text-xs text-white/45 sm:flex-row sm:items-center sm:justify-between">
          <span>Foto, descrição ou perfil informado manualmente.</span>

          <span>Você escolhe como começar.</span>
        </div>
      </motion.div>
    </section>
  )
}

export default HowItWorks