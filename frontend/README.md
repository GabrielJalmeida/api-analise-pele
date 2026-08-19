# Lumina Skin — demonstração pública

Frontend React da experiência de análise cosmética e curadoria de produtos. Ele demonstra como uma aplicação externa pode consumir a API; quem reutilizar o backend pode criar uma interface, marca e jornada próprias.

## Experiência disponível

- análise por fotografia, com descrição complementar opcional;
- análise por texto sem fotografia;
- perfil informado diretamente, sem IA;
- rotina editorial com uma seleção principal por etapa e alternativas;
- detalhes de compatibilidade sem expor score ou porcentagem;
- tratamento honesto de marca, descrição, imagem, conteúdo ou ativos ausentes;
- registro demonstrativo da seleção, sem pagamento;
- histórico associado ao navegador, com consentimento, exclusão e retenção máxima de 365 dias.

A foto é otimizada no navegador antes do envio. A aplicação não contém chaves de IA: toda integração com o provedor ocorre no backend.

## Desenvolvimento

```cmd
npm install
copy .env.example .env
npm run dev
```

Configure o endereço público ou local da API:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Validação

```cmd
npm run lint
npm run build
```

## Produção

Defina `VITE_API_URL` antes do build e inclua o domínio do site em `CORS_ORIGINS` no backend. Variáveis iniciadas por `VITE_` são incorporadas ao frontend e não podem conter segredos.

O histórico desta demonstração não é uma plataforma de e-commerce: não há autenticação de cliente, cobrança, cartão, frete ou confirmação de compra.
