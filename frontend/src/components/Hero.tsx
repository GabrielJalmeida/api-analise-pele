import { motion } from 'motion/react'

interface HeroProps {
    reduzirMovimento: boolean | null
}

function Hero({
    reduzirMovimento,
}: HeroProps) {
    const deslocamento = reduzirMovimento ? 0 : 24

    return (
        <section className="relative flex min-h-screen overflow-hidden">
            <div className="mx-auto grid w-full max-w-7xl items-center gap-12 px-6 pb-16 pt-32 lg:grid-cols-[1.05fr_0.95fr] lg:px-10">
                <div className="relative z-10 max-w-2xl">
                    <motion.p
                        className="mb-6 text-xs font-medium uppercase tracking-[0.32em] text-[#8b7964]"
                        initial={{
                            opacity: 0,
                            y: deslocamento,
                        }}
                        animate={{
                            opacity: 1,
                            y: 0,
                        }}
                        transition={{
                            duration: 0.7,
                            delay: 0.1,
                            ease: 'easeOut',
                        }}
                    >
                        Tecnologia para um cuidado mais pessoal
                    </motion.p>

                    <motion.h1
                        className="font-serif text-5xl leading-[0.98] tracking-[-0.04em] sm:text-6xl lg:text-7xl xl:text-[5.5rem]"
                        initial={{
                            opacity: 0,
                            y: deslocamento,
                        }}
                        animate={{
                            opacity: 1,
                            y: 0,
                        }}
                        transition={{
                            duration: 0.8,
                            delay: 0.2,
                            ease: 'easeOut',
                        }}
                    >
                        Entenda sua pele.

                        <span className="mt-2 block italic text-[#7f8f7a]">
                            Cuide dela melhor.
                        </span>
                    </motion.h1>

                    <motion.p
                        className="mt-8 max-w-xl text-base leading-7 text-[#5f625f] sm:text-lg"
                        initial={{
                            opacity: 0,
                            y: deslocamento,
                        }}
                        animate={{
                            opacity: 1,
                            y: 0,
                        }}
                        transition={{
                            duration: 0.7,
                            delay: 0.35,
                            ease: 'easeOut',
                        }}
                    >
                        Uma experiência simples que interpreta o seu perfil
                        e encontra cuidados compatíveis com você.
                    </motion.p>

                    <motion.div
                        className="mt-10 flex flex-col gap-4 sm:flex-row sm:items-center"
                        initial={{
                            opacity: 0,
                            y: deslocamento,
                        }}
                        animate={{
                            opacity: 1,
                            y: 0,
                        }}
                        transition={{
                            duration: 0.7,
                            delay: 0.5,
                            ease: 'easeOut',
                        }}
                    >
                        <motion.a
                            href="#analise"
                            whileHover={
                                reduzirMovimento
                                    ? undefined
                                    : {
                                        y: -2,
                                    }
                            }
                            whileTap={
                                reduzirMovimento
                                    ? undefined
                                    : {
                                        scale: 0.98,
                                    }
                            }
                            className="rounded-full bg-[#0d1b2a] px-7 py-3.5 text-center text-sm font-medium text-white"
                        >
                            Começar análise
                        </motion.a>

                        <a
                            href="#como-funciona"
                            className="px-2 py-3 text-sm text-[#5f625f] transition-colors hover:text-[#0d1b2a]"
                        >
                            Entender como funciona →
                        </a>
                    </motion.div>

                    <motion.div
                        className="mt-14 flex flex-wrap gap-x-8 gap-y-3 text-xs text-[#7a7d78]"
                        initial={{
                            opacity: 0,
                        }}
                        animate={{
                            opacity: 1,
                        }}
                        transition={{
                            duration: 0.8,
                            delay: 0.65,
                        }}
                    >
                        <span>Sem diagnóstico médico</span>
                        <span>Imagem não armazenada</span>
                        <span>Análise em poucos instantes</span>
                    </motion.div>
                </div>

                <motion.div
                    className="relative min-h-[430px] lg:min-h-[620px]"
                    initial={{
                        opacity: 0,
                        scale: reduzirMovimento ? 1 : 0.97,
                        x: reduzirMovimento ? 0 : 20,
                    }}
                    animate={{
                        opacity: 1,
                        scale: 1,
                        x: 0,
                    }}
                    transition={{
                        duration: 1,
                        delay: 0.25,
                        ease: 'easeOut',
                    }}
                >
                    <div className="absolute inset-0 rounded-[3rem] bg-[#e8dfd3]" />

                    <motion.div
                        className="absolute left-[8%] top-[8%] h-[70%] w-[72%] rounded-[45%_55%_48%_52%/55%_42%_58%_45%] bg-[#d7c6b0]"
                        animate={
                            reduzirMovimento
                                ? undefined
                                : {
                                    y: [0, -8, 0],
                                }
                        }
                        transition={{
                            duration: 8,
                            repeat: Infinity,
                            ease: 'easeInOut',
                        }}
                    />

                    <motion.div
                        className="absolute bottom-[7%] right-[3%] h-[48%] w-[58%] rounded-[55%_45%_58%_42%/42%_55%_45%_58%] bg-[#a9b6a2]"
                        animate={
                            reduzirMovimento
                                ? undefined
                                : {
                                    y: [0, 7, 0],
                                }
                        }
                        transition={{
                            duration: 9,
                            repeat: Infinity,
                            ease: 'easeInOut',
                        }}
                    />

                    <motion.div
                        className="absolute left-[17%] top-[20%] flex h-[58%] w-[58%] items-center justify-center rounded-full border border-white/60 bg-white/35 backdrop-blur-sm"
                        animate={
                            reduzirMovimento
                                ? undefined
                                : {
                                    y: [0, -5, 0],
                                }
                        }
                        transition={{
                            duration: 7,
                            repeat: Infinity,
                            ease: 'easeInOut',
                        }}
                    >
                        <div className="text-center">
                            <span className="block text-xs uppercase tracking-[0.28em] text-[#8b7964]">
                                Lumina
                            </span>

                            <span className="mt-3 block font-serif text-4xl italic text-[#0d1b2a]">
                                skin.
                            </span>
                        </div>
                    </motion.div>

                    <motion.div
                        className="
              absolute bottom-[6%] left-[4%]
              w-[44%] max-w-[230px]
              rounded-2xl
              border border-white/60
              bg-[#f7f5f1]/85
              p-3
              shadow-sm
              backdrop-blur-md
              sm:bottom-[8%] sm:left-[5%] sm:w-[210px] sm:rounded-3xl sm:p-5
              lg:bottom-[11%] lg:w-[230px]
            "
                        initial={{
                            opacity: 0,
                            y: reduzirMovimento ? 0 : 16,
                        }}
                        animate={{
                            opacity: 1,
                            y: 0,
                        }}
                        transition={{
                            duration: 0.7,
                            delay: 0.8,
                            ease: 'easeOut',
                        }}
                    >
                        <p className="text-[10px] uppercase tracking-[0.18em] text-[#8b7964] sm:text-xs sm:tracking-[0.2em]">
                            Sua experiência
                        </p>

                        <p className="mt-2 text-xs leading-5 text-[#3f4846] sm:mt-3 sm:text-sm sm:leading-6">
                            Você conta sobre sua pele. A tecnologia ajuda a
                            encontrar cuidados adequados ao seu perfil.
                        </p>
                    </motion.div>
                </motion.div>
            </div>

            <div className="pointer-events-none absolute -bottom-32 -left-32 h-80 w-80 rounded-full bg-[#f2c6b7]/20 blur-3xl" />
        </section>
    )
}

export default Hero