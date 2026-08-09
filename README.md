# API de Análise de Pele

API backend desenvolvida em Python com FastAPI para análise de perfil de pele e recomendação de produtos cosméticos.

O projeto está em desenvolvimento e faz parte de uma aplicação voltada para e-commerce de cosméticos.

## Funcionalidades atuais

- Cadastro de produtos
- Listagem de produtos
- Busca de produto por ID
- Atualização parcial de produtos
- Validação dos dados recebidos pela API
- Controle de estoque e produtos ativos
- Classificação de produtos por tipo de pele
- Recomendação personalizada com sistema de pontuação
- Organização das recomendações por categoria
- Entrada de texto preparada para futura análise de perfil de pele

## Tecnologias utilizadas

- Python
- FastAPI
- Pydantic
- SQLite
- Uvicorn

## Estrutura do projeto

```text
api-analise-pele/
│
├── main.py
├── models.py
├── services.py
├── database.py
├── criar_banco.py
├── requirements.txt
├── README.md
└── .gitignore
```

### main.py

Contém os endpoints da API e coordena as requisições recebidas.

### models.py

Define os modelos e validações utilizando Pydantic.

### services.py

Contém as regras de negócio, incluindo filtros, cálculo de compatibilidade e geração das recomendações.

### database.py

Responsável pela conexão com o banco de dados SQLite.

### criar_banco.py

Responsável pela criação da estrutura inicial do banco de dados.

## Como executar o projeto

Clone o repositório:

```bash
git clone https://github.com/GabrielJalmeida/api-analise-pele.git
```

Entre na pasta do projeto:

```bash
cd api-analise-pele
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual no Windows:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o banco de dados:

```bash
python criar_banco.py
```

Inicie a API:

```bash
uvicorn main:app --reload
```

A documentação interativa da API estará disponível em:

```text
http://127.0.0.1:8000/docs
```

## Sistema de recomendação

O sistema considera características do perfil de pele e dos produtos disponíveis.

Antes de participar das recomendações, o produto precisa:

- Estar ativo
- Possuir estoque maior que zero
- Ser compatível com o tipo de pele informado ou ser indicado para todos os tipos de pele

A compatibilidade utiliza um sistema de pontuação:

- Tipo de pele correspondente: +3 pontos
- Produto indicado para todos os tipos de pele: +1 ponto
- Compatibilidade com pele sensível: +2 pontos
- Indicação para espinhas: +2 pontos

Os produtos são ordenados pela pontuação e agrupados por categoria.

## Perfil de pele

Atualmente, o perfil utilizado pelo sistema possui três características:

```json
{
  "tipo_pele": "oleosa",
  "sensivel": true,
  "tem_espinha": true
}
```

Os tipos de pele aceitos são:

- oleosa
- seca
- mista
- normal

Esse perfil é utilizado pelo motor de recomendação para selecionar e classificar os produtos.

## Categorias de produtos

Atualmente, a API aceita as seguintes categorias:

- limpeza
- hidratante
- serum
- protetor_solar
- outros

## Banco de dados

O projeto utiliza SQLite.

O arquivo do banco de dados não é enviado ao GitHub.

Para criar um novo banco com a estrutura necessária, execute:

```bash
python criar_banco.py
```

O banco será criado automaticamente no diretório do projeto.

## Validações

A API possui validações para evitar dados inválidos, incluindo:

- Nome de produto vazio
- Nome de produto muito curto ou muito longo
- Preço menor ou igual a zero
- Estoque negativo
- Tipos de pele inválidos
- Categorias inválidas
- Texto de análise muito curto
- Texto de análise com mais de 1000 caracteres
- Produtos duplicados

## Documentação da API

O FastAPI gera automaticamente uma interface Swagger para testes e documentação dos endpoints.

Após iniciar o servidor, acesse:

```text
http://127.0.0.1:8000/docs
```

Os endpoints estão organizados por categorias para facilitar a navegação:

- Geral
- Análise de Pele
- Produtos
- Recomendações

## Status do projeto

🚧 Projeto em desenvolvimento.

A versão atual contém:

- Estrutura da API
- Banco de dados
- CRUD de produtos
- Validações
- Motor de recomendação
- Sistema de pontuação
- Organização das recomendações por categoria
- Entrada de texto preparada para futuras análises

Novas funcionalidades serão adicionadas conforme o desenvolvimento do projeto.