# Sistema de Análise de Pele e Recomendação de Cosméticos

Aplicação desenvolvida em Python com FastAPI para análise cosmética da pele e recomendação de produtos a partir de um catálogo próprio.

O projeto combina inteligência artificial, regras determinísticas de recomendação, gerenciamento de produtos e um painel administrativo desenvolvido em React.

A IA é utilizada para interpretar informações fornecidas pelo usuário, mas **não escolhe diretamente os produtos recomendados**.

O fluxo principal é:

```text
Foto ou descrição
        ↓
      Gemini
        ↓
Perfil estruturado da pele
        ↓
Motor de recomendação da API
        ↓
Produtos do catálogo
```

Também é possível utilizar o sistema sem análise por IA quando o perfil da pele já é conhecido:

```text
Perfil informado diretamente
        ↓
Motor de recomendação
        ↓
Produtos do catálogo
```

> A análise possui finalidade informativa e cosmética. O sistema não realiza diagnóstico médico e não substitui avaliação dermatológica.

---

## Status do projeto

O projeto está atualmente na **Versão 3**.

### Evolução

- **V1** — criação da API e regras iniciais;
- **V2** — integração com IA, evolução do backend e criação do painel administrativo;
- **V3** — reorganização da arquitetura, preparação para exposição da API e desenvolvimento da interface pública;
- **V4** — etapa planejada para finalização, distribuição e acabamento do projeto.

A V3 mantém o painel administrativo criado anteriormente e prepara a aplicação para receber o frontend público.

---

## Funcionalidades

### Análise de pele

O sistema possui três formas independentes de entrada:

- análise por fotografia;
- análise por descrição textual;
- recomendação a partir de um perfil de pele já conhecido.

O frontend pode decidir qual dessas experiências oferecer ao usuário.

### Análise por fotografia

A rota de fotografia:

- aceita JPG, PNG e WEBP;
- limita arquivos a 5 MB;
- limita imagens a 20 megapixels;
- verifica se o arquivo realmente é uma imagem válida;
- sanitiza a imagem antes do envio à IA;
- remove metadados EXIF desnecessários;
- preserva corretamente a orientação da fotografia;
- não armazena a imagem no banco de dados.

### Análise por texto

A IA interpreta a descrição fornecida pelo usuário e tenta gerar um perfil estruturado da pele.

Quando não existem informações suficientes para identificar o perfil, a API retorna explicitamente esse estado em vez de inventar uma classificação.

### Recomendação de produtos

A inteligência artificial **não possui autoridade para selecionar produtos**.

Depois da interpretação do perfil, a decisão é realizada por regras implementadas no backend.

Isso separa duas responsabilidades:

```text
IA
└── interpreta informações

Backend
└── decide quais produtos recomendar
```

Essa arquitetura torna o comportamento mais previsível, testável e controlável.

---

# Painel administrativo

O projeto inclui uma interface administrativa para gerenciamento do catálogo.

Tecnologias:

- React;
- TypeScript;
- Vite;
- Ant Design.

O painel permite:

- cadastrar produtos;
- editar produtos;
- consultar o catálogo;
- pesquisar por nome;
- filtrar por categoria;
- filtrar por tipo de pele;
- filtrar por status;
- desativar produtos;
- reativar produtos;
- acompanhar estoque;
- visualizar produtos ativos e inativos.

A exclusão utiliza **soft delete**.

Isso significa que um produto desativado continua registrado no banco, mas deixa de participar das recomendações.

---

# Tecnologias

## Backend

- Python;
- FastAPI;
- Uvicorn;
- Pydantic;
- SQLite;
- Google Gen AI SDK;
- Pillow;
- python-dotenv.

## Frontend administrativo

- React;
- TypeScript;
- Vite;
- Ant Design;
- ESLint.

## Testes

- Pytest;
- FastAPI TestClient;
- banco SQLite temporário;
- respostas simuladas da IA.

---

# Arquitetura do backend

A aplicação foi organizada utilizando routers para separar as principais responsabilidades.

```text
main.py
│
├── criação da aplicação FastAPI
├── configuração de CORS
├── registro dos routers
└── tratamento global de erros

routers/
│
├── geral.py
│   └── status da aplicação
│
├── produtos.py
│   └── gerenciamento do catálogo
│
├── recomendacoes.py
│   └── recomendação por perfil conhecido
│
└── analise.py
    ├── análise textual
    └── análise de fotografia
```

Outros módulos possuem responsabilidades específicas:

```text
ai_service.py
└── comunicação com o Gemini

services.py
└── regras de negócio e recomendações

database.py
└── conexão e transações SQLite

models.py
└── modelos e validações Pydantic

config.py
└── configurações dependentes do ambiente
```

---

# Estrutura do projeto

```text
analise-pele-V3/
│
├── admin/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProductFilters.tsx
│   │   │   ├── ProductForm.tsx
│   │   │   └── ProductTable.tsx
│   │   │
│   │   ├── services/
│   │   │   └── api.ts
│   │   │
│   │   ├── types/
│   │   │   └── produto.ts
│   │   │
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── main.tsx
│   │   └── index.css
│   │
│   ├── .env.example
│   ├── package.json
│   └── vite.config.ts
│
├── routers/
│   ├── __init__.py
│   ├── analise.py
│   ├── geral.py
│   ├── produtos.py
│   └── recomendacoes.py
│
├── tests/
│   ├── conftest.py
│   ├── test_ai_config.py
│   ├── test_api.py
│   ├── test_config.py
│   ├── test_imagem.py
│   └── test_models.py
│
├── ai_service.py
├── config.py
├── criar_banco.py
├── database.py
├── main.py
├── models.py
├── services.py
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

# Configuração do backend

## 1. Criar o ambiente virtual

Na raiz do projeto:

```powershell
python -m venv .venv
```

No Windows:

```powershell
.venv\Scripts\activate
```

---

## 2. Instalar as dependências

Para executar somente a aplicação:

```powershell
pip install -r requirements.txt
```

Para desenvolvimento e testes:

```powershell
pip install -r requirements-dev.txt
```

---

## 3. Configurar variáveis de ambiente

Crie o arquivo `.env` a partir do exemplo:

```powershell
copy .env.example .env
```

Exemplo:

```env
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-3.5-flash-lite

CORS_ORIGINS=http://localhost:5173
```

Nunca envie a chave real da API para o GitHub.

O arquivo `.env` está ignorado pelo Git.

### Múltiplas origens CORS

As origens podem ser separadas por vírgula:

```env
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,https://exemplo.com
```

Isso permite configurar diferentes frontends sem alterar o código Python.

---

# Funcionamento sem chave de IA

A aplicação consegue iniciar mesmo sem `GEMINI_API_KEY`.

Nesse cenário continuam disponíveis as funcionalidades que não dependem da IA, como:

- CRUD de produtos;
- painel administrativo;
- consulta do catálogo;
- recomendação a partir de um perfil conhecido.

As rotas que realmente precisam do Gemini retornam indisponibilidade enquanto a chave não estiver configurada.

Essa separação permite que o motor de recomendação continue funcionando independentemente do serviço de IA.

---

# Banco de dados

O projeto utiliza SQLite.

Para criar a estrutura inicial:

```powershell
python criar_banco.py
```

O banco local não deve ser enviado para o GitHub.

---

# Executando a API

Na raiz:

```powershell
uvicorn main:app --reload
```

Servidor local:

```text
http://127.0.0.1:8000
```

Documentação interativa:

```text
http://127.0.0.1:8000/docs
```

---

# Rotas principais

## Geral

```text
GET /
GET /status
```

## Produtos

```text
GET    /produto/{id_produto}
GET    /produtos
POST   /produto
PATCH  /produto/{id_produto}
DELETE /produto/{id_produto}
```

`DELETE` realiza desativação lógica do produto.

## Recomendações

```text
POST /recomendacoes
```

Recebe um perfil conhecido e executa o motor determinístico de recomendação.

## Análise de pele

```text
POST /analise-texto
POST /analise-foto
```

Essas são as rotas que utilizam inteligência artificial.

---

# Regras atuais de recomendação

Antes de participar das recomendações, o produto deve:

- estar ativo;
- possuir estoque disponível;
- ser compatível com o tipo de pele informado ou estar marcado para todos os tipos.

A pontuação atual considera:

| Regra | Pontuação |
|---|---:|
| Tipo de pele correspondente | +3 |
| Produto indicado para todos os tipos | +1 |
| Compatível com pele sensível | +2 |
| Indicado para espinhas | +2 |

Depois da pontuação, os produtos são organizados por categoria.

Características como sensibilidade e indicação para espinhas atualmente aumentam a relevância do produto, mas não funcionam como exclusões absolutas.

---

# Segurança e privacidade de imagens

Antes de enviar uma fotografia para análise, a API executa validações de:

- MIME type;
- formato real;
- tamanho do arquivo;
- quantidade de pixels;
- integridade da imagem.

Depois da validação, uma nova representação da imagem é gerada em memória.

Esse processo:

- aplica corretamente a orientação EXIF;
- remove metadados desnecessários;
- evita encaminhar os bytes originais diretamente para a IA.

A aplicação não possui necessidade de armazenar as fotografias analisadas no banco de dados.

---

# Configuração do painel administrativo

Entre na pasta:

```powershell
cd admin
```

Instale as dependências:

```powershell
npm install
```

Crie o `.env`:

```powershell
copy .env.example .env
```

Configuração padrão:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Execute:

```powershell
npm run dev
```

Por padrão, o Vite disponibiliza o painel localmente em:

```text
http://localhost:5173
```

---

# Validação do frontend administrativo

Lint:

```powershell
npm run lint
```

Build de produção:

```powershell
npm run build
```

---

# Testes automatizados

Na raiz do projeto:

```powershell
pytest -v
```

No checkpoint atual da V3:

```text
28 testes aprovados
```

A suíte verifica, entre outros pontos:

- inicialização sem chave de IA;
- indisponibilidade controlada das rotas de IA;
- CRUD de produtos;
- recomendações;
- filtros;
- soft delete;
- análise textual;
- análise de fotografia;
- validação de uploads;
- limite de 5 MB;
- limite de 20 megapixels;
- respostas insuficientes;
- imagens inadequadas;
- padronização dos erros de validação;
- configuração de CORS;
- remoção de EXIF;
- validações dos modelos Pydantic.

Os testes da IA utilizam simulações, portanto a suíte automatizada não precisa consumir quota real do Gemini.

---

# Validação atual

O checkpoint atual da V3 foi validado com:

```text
Backend
28 testes aprovados

Admin
ESLint aprovado
TypeScript aprovado
Build Vite aprovado
```

O Vite atualmente informa um aviso relacionado ao tamanho do bundle de produção.

Esse aviso não impede o funcionamento da aplicação e a divisão do bundle poderá ser realizada posteriormente caso se torne necessária.

---

# Próximas etapas

Durante a V3 serão desenvolvidos os componentes necessários para a experiência pública da aplicação.

Entre os próximos objetivos estão:

- frontend público;
- experiência de análise por fotografia;
- experiência de análise por descrição;
- opção de recomendação sem IA;
- apresentação visual das recomendações;
- preparação da API para publicação;
- proteção das funcionalidades administrativas.

A autenticação das rotas administrativas deve ser implementada antes da exposição pública dessas operações.

Na V4 serão concentradas as etapas finais de acabamento, distribuição e empacotamento do projeto.

---

# Objetivo

Além de seu contexto acadêmico, o projeto é desenvolvido como uma aplicação funcional de portfólio.

O objetivo é demonstrar integração entre:

```text
Frontend
+
API
+
Banco de dados
+
Inteligência artificial
+
Regras de negócio
+
Testes automatizados
```

sem delegar toda a lógica da aplicação à inteligência artificial.