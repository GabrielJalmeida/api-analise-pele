# API de Análise de Pele

Backend em Python com FastAPI para interpretar informações cosméticas da pele e recomendar produtos de um catálogo.

O sistema oferece caminhos independentes de entrada:

- foto, por `POST /analise-foto`;
- descrição em texto, por `POST /analise-texto`;
- perfil já conhecido, por `POST /recomendacoes`.

Nenhum desses caminhos depende dos demais. O frontend decide qual opção apresentar primeiro, se deseja destacar a foto e quais campos serão exigidos na própria experiência. A API apenas valida os dados da rota que foi chamada.

> A análise é informativa e cosmética. Ela não realiza diagnóstico médico e não substitui avaliação dermatológica.

## Funcionalidades

- análise de foto com Gemini e resposta estruturada;
- análise de descrição textual com Gemini e resposta estruturada;
- rejeição de imagens inválidas, excessivamente grandes ou inadequadas para análise;
- cadastro, consulta, listagem e atualização de produtos;
- filtro por estoque, status ativo e compatibilidade com o tipo de pele;
- pontuação e agrupamento de recomendações por categoria;
- validações estritas com Pydantic;
- testes automatizados com banco SQLite temporário e IA simulada.

## Tecnologias

- Python 3.10 ou superior;
- FastAPI e Uvicorn;
- Pydantic;
- SQLite;
- Google Gen AI SDK;
- Pillow;
- Pytest para os testes.

## Configuração local

Entre na pasta do projeto e crie um ambiente virtual:

```bash
python -m venv .venv
```

No Windows, ative-o com:

```powershell
.venv\Scripts\activate
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale as dependências da aplicação:

```bash
pip install -r requirements.txt
```

Crie o arquivo local de configuração a partir do exemplo:

```powershell
copy .env.example .env
```

No arquivo `.env`, informe a chave apenas no servidor:

```dotenv
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-3.5-flash-lite
```

`gemini-3.5-flash-lite` é o modelo padrão do projeto. A variável `GEMINI_MODEL` permite substituí-lo sem editar o código.

A API inicia mesmo sem `GEMINI_API_KEY`. Nesse caso, catálogo, CRUD, perfil direto e recomendações continuam disponíveis; somente as rotas que realmente usam IA respondem com status HTTP 503. Nunca envie a chave para o frontend nem a adicione ao Git.

Crie a estrutura do banco local:

```bash
python criar_banco.py
```

Inicie o servidor:

```bash
uvicorn main:app --reload
```

Documentação interativa:

```text
http://127.0.0.1:8000/docs
```

## Rotas principais

- `POST /analise-foto`: recebe uma imagem JPG, PNG ou WEBP de até 5 MB e 20 megapixels;
- `POST /analise-texto`: recebe uma descrição com ao menos 10 caracteres úteis e até 1000 caracteres no total;
- `POST /perfil-pele`: valida e devolve um perfil informado diretamente;
- `POST /recomendacoes`: recomenda produtos a partir de um perfil já conhecido;
- `GET /recomendacoes/{tipo_pele}`: lista itens compatíveis com o tipo informado;
- `GET /produtos` e `GET /produto/{id}`: consultam o catálogo;
- `POST /produto` e `PATCH /produto/{id}`: cadastram e atualizam itens.

## Regras de recomendação atuais

Antes de participar das recomendações, o produto precisa estar ativo, possuir estoque maior que zero e ser compatível com o tipo de pele informado ou marcado para todos os tipos.

A ordenação usa a seguinte pontuação:

- tipo de pele correspondente: +3;
- produto para todos os tipos: +1;
- compatibilidade com pele sensível: +2;
- indicação para espinhas: +2.

Os produtos são ordenados pela pontuação e agrupados por categoria. Nesta versão, sensibilidade e indicação para espinhas aumentam a pontuação; elas não excluem produtos. Essa semântica deve ser alterada apenas após decisão de negócio.

## Testes

Instale as dependências de desenvolvimento e execute a suíte:

```bash
pip install -r requirements-dev.txt
pytest -q
```

Os testes usam banco temporário e respostas simuladas da IA, portanto não consomem chave nem quota do Gemini.

## Estrutura

```text
api-analise-pele/
├── ai_service.py
├── criar_banco.py
├── database.py
├── main.py
├── models.py
├── services.py
├── tests/
├── .env.example
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Limites desta etapa

Esta é uma versão de desenvolvimento para o TCC. Antes de produção, ainda será necessário proteger as rotas administrativas, definir CORS, usar armazenamento persistente adequado ao ambiente de hospedagem, aplicar política de privacidade para fotos e adicionar observabilidade. Essas melhorias fazem parte das próximas etapas do plano do projeto.
