# Relatório de validação da Versão 4

## Escopo

A Versão 4 mantém três componentes executados localmente e de forma independente:

- API FastAPI;
- frontend público Lumina Skin;
- painel administrativo Skin Admin no navegador.

O escopo final é exclusivamente web/local: API, frontend público e painel administrativo executados separadamente durante o desenvolvimento.

## Backend

Comandos de validação:

```powershell
python -m pytest -q --basetemp .pytest-build-temp
python -m compileall -q main.py config.py models.py services.py routers tests
```

A suíte cobre rotas públicas e administrativas, contratos dos provedores de IA, catálogo, imagens, importação, pedidos demonstrativos, histórico, retenção e regras de recomendação.

## Frontend Lumina

```powershell
Set-Location frontend
npm install
npm run lint
npm run build
```

O frontend consome a URL definida em `VITE_API_URL` e não contém chaves de IA.

## Skin Admin

```powershell
Set-Location admin
npm install
npm run lint
npm run build
```

O painel administra a API configurada em `VITE_API_URL`. Chaves e modelos de IA são definidos somente no `.env` do backend.

## Critério de entrega

A V4 está pronta para publicação no repositório quando:

- todos os testes Python passam;
- frontend e admin passam em TypeScript/lint/build após instalação limpa das dependências;
- o repositório contém apenas os componentes necessários para API, frontend e painel administrativo;
- `.env`, bancos locais, ambientes virtuais, `node_modules`, `dist`, caches e logs não são versionados;
- a execução local documentada no README inicia API, frontend e painel administrativo separadamente.
