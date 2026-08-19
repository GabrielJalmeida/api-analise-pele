# Skin Admin — Versão X

Painel administrativo local do sistema de análise de pele. Ele gerencia o catálogo, imagens, importações, configurações de IA e registros demonstrativos usando a API FastAPI.

## Dois modos de uso

- **Desenvolvimento:** React/Vite no navegador, apontando para uma API já iniciada.
- **Aplicativo Windows:** Tauri abre o painel em uma janela própria e inicia a API local empacotada como sidecar. Banco, mídias e configuração pertencem àquela instalação.

O aplicativo instalado não altera a demonstração hospedada. Na primeira abertura, o banco local começa vazio.

## Funcionalidades

- cadastro, edição, busca, ativação e desativação de produtos;
- apenas nome, preço, categoria e tipo de pele são obrigatórios;
- upload e substituição de imagens processadas pelo backend;
- importação com prévia por CSV/XLSX, até 1.000 itens;
- organização de texto desestruturado com IA, até 100 itens;
- política explícita para ignorar ou atualizar nomes duplicados;
- consulta de pedidos demonstrativos retidos por até 365 dias;
- configuração local de Gemini, OpenAI ou Claude;
- opção de reduzir estoque ao registrar uma seleção, desativada por padrão.

## Desenvolvimento

Com a API em `http://127.0.0.1:8000`:

```cmd
npm install
copy .env.example .env
npm run dev
```

Para validar:

```cmd
npm run lint
npm run build
```

## Aplicativo Windows

Na raiz do repositório, execute:

```cmd
build_windows.bat
```

O processo testa e empacota a API com PyInstaller, compila o painel e gera um instalador NSIS com Tauri 2. Consulte [`../docs/GUIA_DESKTOP.md`](../docs/GUIA_DESKTOP.md).

## Segurança

As operações administrativas são bloqueadas quando `APP_ENV=production`. O modo desktop usa uma API restrita a `127.0.0.1` e armazena a chave de IA localmente sem devolvê-la pela interface.

Isso não equivale a autenticação para um painel web. Quem decidir publicar este painel deve implementar identidade, autorização, proteção contra abuso e auditoria.
