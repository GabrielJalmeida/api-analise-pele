# Skin Admin — Versão 4

Painel React/Vite que administra uma instância da API FastAPI pelo navegador.

## Funcionalidades

- cadastro, edição, busca, ativação e desativação de produtos;
- upload e substituição de imagens processadas pelo backend;
- importação com prévia por CSV/XLSX;
- organização de texto por IA quando o backend possui credencial;
- política para ignorar ou atualizar produtos duplicados;
- consulta de pedidos demonstrativos.

## Executar

Primeiro inicie a API na raiz do repositório. Depois:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Configure a URL da API em `.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

As credenciais e os modelos de IA pertencem ao backend e devem ser definidos no `.env` da raiz. Nenhuma chave é armazenada no bundle do painel.

## Validar

```powershell
npm run lint
npm run build
```

## Segurança

Com `APP_ENV=production`, a API oculta as operações administrativas. O painel atual é destinado ao uso local com `APP_ENV=development`.

Não publique este painel sem implementar autenticação, autorização e auditoria no backend. CORS, sozinho, não é controle de acesso.
