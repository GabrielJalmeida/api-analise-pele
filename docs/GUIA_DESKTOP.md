# Guia do aplicativo desktop

## Resultado

O Skin Admin é uma janela Tauri que inicia uma API FastAPI local em `127.0.0.1:8765`. O backend é um executável PyInstaller incluído como sidecar. O usuário final não precisa abrir terminal, navegador, Python ou Node.js.

Cada instalação mantém separadamente:

```text
config/.env
data/produtos.db
media/produtos/
lumina-api.log
```

O diretório-base é escolhido pelo Tauri no armazenamento local do aplicativo. O banco nasce vazio e o painel não se conecta à demonstração pública.

## Requisitos de build no Windows

- Windows 10 ou 11;
- Python 3.12;
- Node.js LTS;
- Rust estável e Cargo;
- Microsoft C++ Build Tools exigidos pelo Tauri;
- WebView2, normalmente já presente no Windows moderno.

## Build local

Abra o Prompt de Comando na raiz do projeto:

```cmd
build_windows.bat
```

O script:

1. cria `.venv-build`;
2. instala as dependências de desktop;
3. executa os testes da API;
4. gera `dist\lumina-api.exe`;
5. copia o sidecar com o nome esperado pelo Tauri;
6. instala as dependências do painel com `npm ci`;
7. compila o instalador NSIS.

Saída principal:

```text
admin\src-tauri\target\release\bundle\nsis\*-setup.exe
```

## Build no GitHub

O workflow `Build Skin Admin para Windows` é manual. Em **Actions**, selecione o workflow, execute **Run workflow** e baixe o artefato `skin-admin-versao-x-windows` ao final.

## Primeiro uso

1. instale e abra o Skin Admin;
2. abra **Inteligência artificial**;
3. escolha Gemini, OpenAI ou Claude;
4. informe um modelo disponível em sua conta e a chave correspondente;
5. cadastre produtos individualmente ou use **Importar catálogo**.

A chave é salva no computador e não aparece novamente na resposta da API. Faça backup do diretório local caso precise preservar catálogo, imagens e histórico.

## Limites de distribuição

O instalador não é assinado com certificado comercial. O SmartScreen pode apresentar aviso. Publicação comercial também exige política de atualizações, assinatura de código, backup, suporte e avaliação legal própria.
