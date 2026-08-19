# Privacidade e limites

Este software é uma demonstração técnica e não substitui aconselhamento jurídico, dermatológico ou uma plataforma de comércio eletrônico.

## Fotografias e descrições

- a aplicação processa a fotografia em memória e não a grava no banco ou na pasta de mídias;
- a imagem e o texto são enviados ao provedor de IA configurado;
- cada operador deve consultar os termos do provedor e informar o usuário de forma adequada;
- não use o sistema para diagnóstico, emergência ou decisão médica;
- qualidade da câmera, iluminação, maquiagem, enquadramento e região fotografada alteram o resultado.

## Histórico demonstrativo

- não são solicitados dados de cartão;
- o registro só ocorre após consentimento explícito;
- nome, e-mail, itens e preços são mantidos por no máximo 365 dias;
- o token aleatório do navegador é armazenado apenas como hash SHA-256;
- o usuário pode excluir o próprio histórico pelo mesmo navegador;
- registros expirados são removidos em consultas, na inicialização e periodicamente.

O token do navegador não é autenticação de identidade. Para compras reais, implemente contas, autorização, recuperação de acesso, pagamento, antifraude, frete, cancelamento e obrigações legais aplicáveis.

## Painel

No aplicativo instalado, dados e chave de IA ficam no computador local. Na API pública, rotas administrativas são ocultadas em `APP_ENV=production`. Não publique o painel web sem autenticação e autorização reais.

## Operação

SQLite e arquivos locais são adequados para demonstração e uso individual. Ambientes com múltiplas instâncias ou alto volume devem usar banco de servidor, armazenamento de objetos, backup, monitoramento e gestão de segredos.
