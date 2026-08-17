# Lumina Skin — Análise de Pele e Recomendação de Cosméticos

Aplicação full stack para interpretar características cosméticas da pele e revelar uma curadoria de produtos compatíveis com o perfil informado.

O projeto combina um backend em FastAPI, inteligência artificial Gemini, regras determinísticas de recomendação, catálogo próprio com 50 produtos, frontend público e painel administrativo.

> A análise possui finalidade informativa e cosmética. O sistema não realiza diagnóstico médico e não substitui avaliação dermatológica.

## Versão atual

**v3.8.0 — frontend público, catálogo visual e publicação da aplicação.**

- Site público: [https://lumina-skin-lyart.vercel.app](https://lumina-skin-lyart.vercel.app)
- API: [https://api-production-f6fd.up.railway.app](https://api-production-f6fd.up.railway.app)
- Documentação da API: [https://api-production-f6fd.up.railway.app/docs](https://api-production-f6fd.up.railway.app/docs)

O painel administrativo permanece local nesta versão. As operações administrativas de escrita são bloqueadas no ambiente público enquanto não houver autenticação.

## Como o sistema funciona

O usuário pode escolher livremente entre três caminhos independentes:

- enviar uma fotografia;
- descrever a pele por texto;
- informar diretamente um perfil conhecido, sem utilizar IA.

A fotografia não é obrigatória. O frontend decide como apresentar e destacar cada opção, enquanto o backend valida apenas os dados da rota utilizada.

```text
Foto ou descrição
        ↓
      Gemini
        ↓
Perfil estruturado da pele
        ↓
Motor determinístico da API
        ↓
Curadoria de produtos compatíveis
```

A IA interpreta as informações, mas **não escolhe produtos**. A seleção do catálogo é executada por regras controladas e testáveis no backend.

## Funcionalidades da v3.8.0

### Experiência pública

- interface responsiva em React, TypeScript, Vite, Tailwind CSS e Motion;
- análise por fotografia;
- análise por descrição textual;
- recomendação sem IA a partir de perfil informado diretamente;
- tratamento de informações insuficientes e assuntos fora do escopo;
- confirmação do tipo de pele quando fotografia e texto apresentam resultados diferentes;
- observações visuais intermediárias durante o resultado da fotografia;
- recomendações organizadas por categoria;
- cards com imagem, marca, nome, descrição, conteúdo, preço, ativos e motivos de compatibilidade;
- identidade visual própria da Lumina Skin.

### Análise por fotografia

- aceita JPG, PNG e WEBP;
- limita arquivos a 5 MB e imagens a 50 megapixels;
- verifica MIME type, formato real e integridade do arquivo;
- corrige a orientação EXIF;
- remove metadados desnecessários;
- reduz dimensões antes do envio à IA;
- não armazena a fotografia analisada.

A leitura visual pode observar:

- tipo de pele e confiança da classificação;
- espinhas;
- marcas pós-acne;
- vermelhidão;
- descamação;
- brilho excessivo.

Sensibilidade não é inferida exclusivamente pela imagem. Quando informada, ela vem da descrição complementar do usuário.

### Análise por texto

A IA interpreta a descrição e tenta estruturar:

- tipo de pele;
- sensibilidade;
- presença de espinhas.

O fluxo distingue respostas válidas, informações insuficientes e conteúdo fora do domínio. Também possui proteções contra sujeito não humano e instruções adversariais.

### Catálogo e recomendações

O catálogo da demonstração contém 50 produtos distribuídos entre:

- limpeza;
- sérum;
- hidratação;
- proteção solar;
- outros cuidados.

Antes de participar das recomendações, o produto precisa estar ativo, possuir estoque e ser compatível com o tipo de pele informado ou marcado para todos os tipos.

| Regra | Pontuação |
|---|---:|
| Tipo de pele correspondente | +3 |
| Produto indicado para todos os tipos | +1 |
| Compatível com pele sensível | +2 |
| Indicado para espinhas | +2 |

A pontuação determina a ordem interna das recomendações, mas não é apresentada ao usuário final.

### Imagens dos produtos

O painel administrativo permite enviar imagens JPG, PNG ou WEBP. O backend:

- valida arquivos de até 10 MB e 40 megapixels;
- corrige orientação EXIF;
- limita a maior dimensão a 1600 pixels;
- converte a imagem para WebP;
- gera um nome seguro com identificador único;
- publica o arquivo em `/media/produtos/{categoria}/...`.

## Painel administrativo

O projeto inclui um painel local desenvolvido com React, TypeScript, Vite e Ant Design.

Ele permite:

- cadastrar e editar produtos;
- enviar imagens;
- consultar e pesquisar o catálogo;
- filtrar por categoria, tipo de pele e status;
- acompanhar estoque;
- desativar e reativar produtos.

A exclusão utiliza soft delete: o produto permanece no banco, mas deixa de participar das recomendações.

## Tecnologias

### Backend

- Python;
- FastAPI e Uvicorn;
- Pydantic;
- SQLite;
- Google Gen AI SDK;
- Pillow;
- python-dotenv;
- Pytest.

### Frontend público

- React;
- TypeScript;
- Vite;
- Tailwind CSS;
- Motion.

### Painel administrativo

- React;
- TypeScript;
- Vite;
- Ant Design.

### Hospedagem

- frontend público na Vercel;
- backend e volume persistente na Railway;
- SQLite armazenado no volume da aplicação.

## Estrutura principal

```text
analise-pele-V3/
├── admin/                    # painel administrativo local
├── frontend/                 # interface pública
├── media/produtos/           # imagens do catálogo
├── routers/
│   ├── analise.py
│   ├── geral.py
│   ├── produtos.py
│   └── recomendacoes.py
├── tests/
├── ai_service.py             # comunicação com o Gemini
├── config.py                 # configuração por ambiente
├── criar_banco.py
├── database.py
├── main.py
├── models.py
├── popular_catalogo.py       # carga automatizada do catálogo
├── product_image_service.py  # processamento de imagens de produto
├── services.py               # regras de recomendação
├── railway.json
├── requirements.txt
└── README.md
```

## Configuração local do backend

Na raiz do projeto, crie e ative o ambiente virtual:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```cmd
python -m pip install -r requirements.txt
```

Para desenvolvimento e testes:

```cmd
python -m pip install -r requirements-dev.txt
```

Crie o arquivo local de configuração:

```cmd
copy .env.example .env
```

Exemplo:

```env
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-3.5-flash-lite
APP_ENV=development
DATABASE_PATH=produtos.db
CORS_ORIGINS=http://localhost:5173
```

Nunca envie a chave real ao GitHub ou ao frontend.

Crie o banco e, se desejar o catálogo de demonstração, execute:

```cmd
python criar_banco.py
python popular_catalogo.py --aplicar
```

Inicie a API:

```cmd
uvicorn main:app --reload
```

Endereços locais:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

## Configuração do frontend público

```cmd
cd frontend
npm install
copy .env.example .env
npm run dev
```

Configuração local:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Build de produção:

```cmd
npm run build
```

## Configuração do painel administrativo

```cmd
cd admin
npm install
copy .env.example .env
npm run dev
```

Configuração local:

```env
VITE_API_URL=http://127.0.0.1:8000
```

O painel não deve ser disponibilizado publicamente antes da implementação de autenticação.

## Rotas principais

```text
GET    /
GET    /status

GET    /produto/{id_produto}
GET    /produtos
POST   /produto
PATCH  /produto/{id_produto}
DELETE /produto/{id_produto}
POST   /produtos/imagem

POST   /perfil-pele
POST   /analise-texto
POST   /analise-foto
POST   /recomendacoes
```

As rotas administrativas de escrita permanecem disponíveis no desenvolvimento local e são ocultadas no ambiente público da v3.8.0.

## Testes e builds

Checkpoint da v3.8.0:

```text
Backend:          35 testes aprovados
Frontend público: build aprovado
Admin:            build aprovado
```

Execute a suíte do backend com:

```cmd
python -m pytest -q
```

Os testes usam banco temporário e respostas simuladas da IA, portanto não consomem chave nem quota do Gemini.

Existem dois avisos externos conhecidos relacionados ao TestClient/HTTPX e ao Google Gen AI SDK. Eles não impedem a execução dos testes.

## Variáveis utilizadas em produção

Backend:

```env
APP_ENV=production
DATABASE_PATH=/data/produtos.db
GEMINI_API_KEY=chave_configurada_no_servidor
GEMINI_MODEL=gemini-3.5-flash-lite
CORS_ORIGINS=https://lumina-skin-lyart.vercel.app
```

Frontend:

```env
VITE_API_URL=https://api-production-f6fd.up.railway.app
```

## Limites conhecidos desta versão

A v3.8.0 é uma versão funcional para demonstração acadêmica e portfólio. Permanecem planejados para a auditoria técnica da V4:

- autenticação e autorização do painel administrativo;
- tratamento automático de imagens órfãs;
- auditoria de instalação limpa e dependências;
- observabilidade e tratamento ampliado de falhas transitórias de rede;
- revisão da persistência e dos uploads para produção;
- otimização do bundle do painel;
- revisão completa de segurança e documentação.

Em hospedagens gratuitas, reinicializações e oscilações ocasionais de rede podem exigir uma nova tentativa da solicitação.

## Evolução do projeto

- **V1** — API e regras iniciais de recomendação;
- **V2** — integração com IA, estabilização do backend e painel administrativo;
- **V3.0 alpha** — preparação da arquitetura para a experiência pública;
- **V3.8.0** — frontend público, catálogo visual completo e aplicação hospedada;
- **V4** — auditoria técnica e endurecimento para uso externo;
- **V5** — melhorias orientadas por feedback e finalização.

## Objetivo

Além de seu contexto acadêmico, o projeto demonstra a integração entre frontend, API, banco de dados, inteligência artificial, processamento de imagens, regras de negócio e testes automatizados, sem delegar toda a decisão do sistema à IA.
