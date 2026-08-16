# Skin Admin

Painel administrativo do Sistema de Análise de Pele e Recomendação de Cosméticos.

Esta interface é responsável pelo gerenciamento do catálogo de produtos utilizado pela API.

## Tecnologias

- React
- TypeScript
- Vite
- Ant Design
- ESLint

## Funcionalidades

O painel permite:

- cadastrar produtos;
- editar produtos;
- pesquisar produtos por nome;
- filtrar por categoria;
- filtrar por tipo de pele;
- visualizar produtos ativos e inativos;
- desativar produtos;
- reativar produtos;
- acompanhar preço e estoque.

A desativação utiliza soft delete. O produto continua registrado no banco de dados, mas deixa de participar das recomendações enquanto estiver inativo.

## Comunicação com a API

O painel não acessa o banco SQLite diretamente.

O fluxo é:

```text
React
  ↓ HTTP/JSON
FastAPI
  ↓
SQLite
```

O endereço da API é configurado através da variável:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Configuração

Instale as dependências:

```powershell
npm install
```

Crie o arquivo local de ambiente:

```powershell
copy .env.example .env
```

O arquivo `.env.example` possui a configuração padrão:

```env
VITE_API_URL=http://127.0.0.1:8000
```

O `.env` local não deve ser enviado para o GitHub.

## Desenvolvimento

Com a API FastAPI em execução, inicie o painel:

```powershell
npm run dev
```

Por padrão:

```text
http://localhost:5173
```

## Validação

Executar o lint:

```powershell
npm run lint
```

Gerar o build de produção:

```powershell
npm run build
```

## Segurança

O painel administrativo foi desenvolvido inicialmente para utilização controlada durante o desenvolvimento do projeto.

Antes da exposição pública das operações administrativas, deverá ser implementado um mecanismo de autenticação e autorização.