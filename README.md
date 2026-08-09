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
- Entrada de texto para futura análise de perfil de pele

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
└── .gitignore