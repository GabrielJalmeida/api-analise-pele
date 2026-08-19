# Privacidade e limites

Este software é uma demonstração técnica e não substitui aconselhamento jurídico, dermatológico ou uma plataforma de comércio eletrônico.

## Fotografias e descrições

- a fotografia é processada em memória e não é gravada no banco ou na pasta de mídias;
- imagem e texto são enviados ao provedor de IA configurado no backend;
- o operador deve consultar os termos do provedor e informar o usuário;
- o sistema não deve ser usado para diagnóstico, emergência ou decisão médica;
- câmera, iluminação, maquiagem e enquadramento alteram o resultado.

## Pedidos demonstrativos

- nenhum dado de cartão é solicitado ou armazenado;
- o registro ocorre após consentimento explícito;
- nome, e-mail, itens e preços são mantidos por no máximo 365 dias;
- o token aleatório do navegador é armazenado apenas como hash SHA-256;
- registros expirados são removidos em consultas, na inicialização e periodicamente.

O token do navegador não prova identidade. Para compras reais, implemente contas, autorização, pagamento, antifraude, frete, cancelamento e as obrigações legais aplicáveis.

## Painel

O painel é um cliente web da API e não armazena chaves de IA. As rotas administrativas são ocultadas em `APP_ENV=production` porque o projeto ainda não possui autenticação administrativa.

Não publique o painel sem identidade, autorização, auditoria e proteção contra abuso.

## Operação

SQLite e arquivos locais são adequados para demonstração e instância única. Ambientes distribuídos ou de alto volume devem usar banco de servidor, armazenamento de objetos, backup, monitoramento e gestão de segredos.
