EXEMPLO DE INTEGRAÇÃO
=====================

1. Inicie a API FastAPI na porta 8000.
2. No .env do backend, inclua:
   CORS_ORIGINS=http://localhost:5500
3. Reinicie a API.
4. Abra um terminal nesta pasta e execute:
   python -m http.server 5500
5. Abra http://localhost:5500 no navegador.

Arquivos:
- index.html: estrutura e formulários;
- styles.css: apresentação;
- app.js: requisições, erros e renderização.

O exemplo começa apontando para http://127.0.0.1:8000. É possível alterar
o endereço no topo da página. A opção fica salva somente no navegador.

Nunca coloque uma chave de IA nestes arquivos.
