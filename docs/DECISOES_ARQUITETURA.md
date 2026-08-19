# Decisões de arquitetura

## API como núcleo

Frontend Lumina e Skin Admin são clientes HTTP independentes. Ambos apontam para uma API FastAPI por variável de ambiente e nenhum deles inicia ou empacota o backend.

## Clientes web independentes

Frontend Lumina e Skin Admin rodam como aplicações web separadas e se comunicam com a API somente por HTTP. Isso mantém um único contrato de execução e simplifica desenvolvimento, testes e manutenção local.

## IA interpreta; backend recomenda

Gemini, OpenAI ou Claude transforma texto/foto em um perfil estruturado. A escolha dos produtos continua determinística no backend, tornando o resultado explicável e testável.

Chaves e modelos pertencem ao ambiente do servidor. O painel web não recebe nem grava segredos.

## Entradas independentes

Foto, texto e perfil manual são caminhos separados. O frontend decide a experiência; a API valida apenas a rota utilizada.

## Administração local

Sem um sistema de identidade, as rotas administrativas ficam disponíveis apenas em `APP_ENV=development` e são ocultadas em produção. Publicar o painel exige autenticação e autorização reais no backend.

## Banco vazio por padrão

Produtos fictícios servem somente à demonstração. O banco pode receber dados por formulário, CSV, XLSX ou texto organizado por IA.

## Histórico não é checkout

O módulo registra uma seleção demonstrativa. Ele não processa pagamento nem armazena cartão. A redução de estoque permanece opcional.

## Escala futura

SQLite e mídias locais simplificam uma instância única. Uma implantação com múltiplas réplicas deve usar banco de servidor e armazenamento de objetos.
