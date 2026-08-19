# Relatório de validação da Versão X

Este arquivo registra o checklist técnico reproduzível da entrega, executado em 18 de agosto de 2026.

## Backend

```cmd
python -m pytest -q
python -m compileall -q .
```

Verificações cobertas pela suíte incluem rotas existentes, contratos dos provedores, campos opcionais, importação, pedidos, retenção, configuração desktop e ciclo de imagens.

**Resultado da entrega:** 62 testes aprovados. Compilação dos módulos Python aprovada.

## Frontend público

```cmd
cd frontend
npm ci
npm run lint
npm run build
```

**Resultado da entrega:** lint aprovado e build Vite aprovado. JavaScript principal com aproximadamente 393 kB antes de gzip.

## Painel

```cmd
cd admin
npm ci
npm run lint
npm run build
npm run build:desktop
```

**Resultado da entrega:** ESLint aprovado; builds web e desktop aprovados. A divisão de chunks manteve o maior arquivo abaixo de 200 kB antes de gzip.

## Backend empacotado

```cmd
python -m PyInstaller --noconfirm --clean desktop_api.spec
```

O executável deve ser iniciado com um diretório temporário e validado em `/status`, `/produtos` e pela integridade do SQLite.

**Resultado da entrega no ambiente Linux de validação:** executável one-file iniciado com sucesso; status da Versão X, banco vazio, cadastro mínimo, recomendação, criação das tabelas e `PRAGMA integrity_check` aprovados.

## Instalador Windows

A configuração Tauri, ícones, permissões e sidecar fazem parte do repositório e seus arquivos JSON/TOML foram validados. A compilação final do instalador deve ocorrer em Windows pelo `build_windows.bat` ou pelo workflow manual do GitHub, pois o instalador NSIS e o sidecar `.exe` são específicos dessa plataforma.
