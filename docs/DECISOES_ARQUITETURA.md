# Decisões de arquitetura

## IA interpreta; backend recomenda

Gemini, OpenAI ou Claude transforma texto/foto em um perfil estruturado. A escolha dos produtos continua determinística no backend, o que torna o resultado explicável e testável.

## Entradas independentes

Foto, texto e perfil manual são caminhos separados. O frontend decide qual experiência destacar; a API valida apenas a rota utilizada. Uma fotografia de região parcial pode produzir observações locais, desde que haja informação suficiente.

## Frontend público é demonstração

A Lumina Skin mostra uma integração completa, mas não faz parte do contrato obrigatório. Qualquer consumidor pode usar as rotas da API em outro frontend.

## Administração local

O Skin Admin instalado administra uma API, um banco e mídias locais. Isso dá autonomia a quem clona o projeto e evita expor um painel sem autenticação. Dados locais e dados da demonstração hospedada não são sincronizados.

## Banco vazio por padrão

Produtos fictícios servem apenas para demonstração. Uma nova instalação começa vazia e pode receber dados por formulário, CSV, XLSX ou texto organizado por IA.

## Histórico não é checkout

O módulo registra uma seleção para demonstrar persistência e integração. Ele não finge pagamento nem guarda cartão. A redução de estoque permanece opt-in porque não existe confirmação financeira.

## Escala futura

SQLite e mídias locais simplificam a distribuição individual. Uma implantação de produção pode substituir esses componentes por PostgreSQL e armazenamento de objetos sem exigir que o frontend Lumina seja adotado.
