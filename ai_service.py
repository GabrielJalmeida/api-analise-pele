import os
import base64
from functools import lru_cache

from pydantic import ValidationError
from dotenv import load_dotenv
from google import genai
from google.genai import errors

from models import ResultadoAnaliseIA, ResultadoAnaliseFoto

load_dotenv()

# Modelo padrão informado para o projeto. Ele pode ser alterado por ambiente
# sem exigir mudanças no código-fonte.
MODELO_GEMINI = "gemini-3.5-flash-lite"

class LimiteIAExcedido(Exception):
    pass

class ServicoIAIndisponivel(Exception):
    pass

class RespostaIAInvalida(Exception):
    pass

class ConfiguracaoIAInvalida(Exception):
    pass


def obter_modelo_gemini():
    modelo_configurado = os.getenv("GEMINI_MODEL", MODELO_GEMINI).strip()
    return modelo_configurado or MODELO_GEMINI


@lru_cache(maxsize=4)
def _criar_cliente(api_key):
    return genai.Client(api_key=api_key)


def obter_cliente():
    """Cria o cliente somente quando uma análise por IA é solicitada."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        raise ConfiguracaoIAInvalida(
            "A variável de ambiente GEMINI_API_KEY não foi configurada"
        )

    return _criar_cliente(api_key)

def interpretar_perfil(texto):
    prompt = f"""
Analise somente as informações fornecidas pelo usuário sobre a própria pele.

Determine:
- tipo de pele: oleosa, seca, mista ou normal
- se a pele é sensível
- se há relato de espinhas

Regras importantes:

- Não invente informações.
- Se uma característica não puder ser determinada pelo texto, retorne null.
- Não considere ausência de informação como false.
- Não considere ausência de informação como pele normal.
- Use apenas informações fornecidas ou claramente sustentadas pela descrição do usuário.
- Prefira null a uma suposição sem evidência suficiente.

Descrição do usuário:
{texto}
"""

    client = obter_cliente()

    try:
        interaction = client.interactions.create(
            model=obter_modelo_gemini(),
            input=prompt,
            store=False,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": ResultadoAnaliseIA.model_json_schema()
            }
        )

    except errors.ClientError as erro:
        if getattr(erro, "code", None) == 429:
            raise LimiteIAExcedido from erro

        raise ConfiguracaoIAInvalida from erro

    except errors.ServerError as erro:
        raise ServicoIAIndisponivel from erro

    try:
        resultado = ResultadoAnaliseIA.model_validate_json(
            interaction.output_text
        )

    except ValidationError as erro:
        raise RespostaIAInvalida from erro

    return resultado

def interpretar_foto(conteudo, mime_type):
    imagem_base64 = base64.b64encode(conteudo).decode("utf-8")

    prompt = """
Analise somente características visualmente observáveis da pele na imagem.

Primeiro determine se a imagem é adequada para análise cosmética visual da pele.

Considere a imagem inadequada quando, por exemplo:
- não houver pele facial suficientemente visível;
- a imagem estiver muito escura, desfocada ou distante;
- houver água cobrindo significativamente a pele;
- maquiagem, filtro ou outro fator impedir uma avaliação confiável.

Se a imagem for adequada, avalie:
- tipo de pele: oleosa, seca, mista ou normal;
- presença de espinhas visíveis;
- presença de marcas visíveis compatíveis com pós-acne;
- vermelhidão visível;
- descamação visível;
- brilho excessivo visível.

Regras importantes:
- Não invente informações.
- Use null quando uma característica não puder ser determinada com segurança.
- Não use false apenas porque algo não foi mencionado ou não ficou claro.
- false significa que há evidência visual suficiente para considerar a característica ausente.
- Não classifique pele como oleosa apenas por brilho.
- Brilho pode ser causado por iluminação, suor, água, maquiagem ou cosméticos.
- Não inferir sensibilidade da pele pela aparência.
- Espinhas ativas e marcas pós-acne são características diferentes.
- Prefira null a uma suposição.
- Se imagem_adequada for true, motivo_inadequacao deve ser null.
- Se imagem_adequada for false, informe o principal motivo da inadequação.
- Use somente um destes motivos:
  sem_rosto_visivel,
  rosto_distante,
  imagem_escura,
  imagem_desfocada,
  iluminacao_irregular,
  pele_molhada,
  interferencia_visual,
  outro.
- Quando imagem_adequada for false, as características da pele devem ser null.
- Considere a imagem inadequada se filtros, efeitos, maquiagem intensa,
  tinta, produtos visíveis ou outras interferências alterarem a aparência
  natural da pele.

- Considere a imagem inadequada quando sombras fortes, luz direta intensa,
  áreas superexpostas ou iluminação irregular impedirem uma avaliação confiável.

- Não atribua a causa exata de uma interferência visual se ela não puder
  ser determinada com segurança.

- Para características sutis, como marcas pós-acne pouco visíveis, use null
  quando a resolução, iluminação ou distância não permitirem confirmar
  nem descartar a característica com segurança.

- Não use "mista" como classificação padrão quando o tipo de pele estiver incerto.
- Classifique como "mista" somente quando houver evidência visual simultânea de comportamentos diferentes em regiões distintas do rosto, por exemplo maior oleosidade na zona T e aparência normal ou seca em outras regiões.
- Se não houver evidência visual suficiente para distinguir oleosa, seca, mista ou normal, retorne null.
- Não determine o tipo de pele apenas pela textura, poros, tom da pele ou pequenas imperfeições.

- Brilho causado aparentemente por iluminação não deve ser classificado como brilho_excessivo.
- Use brilho_excessivo=true somente quando houver evidência visual clara e distribuída de brilho na superfície da pele que não seja explicada principalmente pela iluminação.
- Se não for possível distinguir brilho natural da pele de reflexo da iluminação, use null.

- Use tem_espinha=true somente quando houver lesões visualmente compatíveis com espinhas ativas com evidência suficiente.
- Não classifique sardas, pintas, manchas planas, cicatrizes, marcas de pigmentação ou pequenas irregularidades indefinidas como espinhas.
- Se houver uma alteração visual mas não for possível determinar com segurança se é uma espinha, use null.
"""

    client = obter_cliente()

    try:
        interaction = client.interactions.create(
            model=obter_modelo_gemini(),
            store=False,
            input=[
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image",
                    "data": imagem_base64,
                    "mime_type": mime_type
                }
            ],
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": ResultadoAnaliseFoto.model_json_schema()
            }
        )
    except errors.ClientError as erro:
        if getattr(erro, "code", None) == 429:
            raise LimiteIAExcedido from erro

        raise ConfiguracaoIAInvalida from erro

    except errors.ServerError as erro:
        raise ServicoIAIndisponivel from erro

    try:
        resultado = ResultadoAnaliseFoto.model_validate_json(
            interaction.output_text
        )

    except ValidationError as erro:
        raise RespostaIAInvalida from erro

    return resultado

