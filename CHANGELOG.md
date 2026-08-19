# Changelog

## Versão X — edição especial

### Experiência pública

- apresentação das recomendações reconstruída como rotina editorial;
- uma seleção principal por categoria e alternativas secundárias;
- detalhes de compatibilidade sem exibir a pontuação interna;
- estados apropriados para dados editoriais ausentes;
- fotografia otimizada antes do envio e aquecimento da API;
- histórico demonstrativo consultável e removível pelo navegador.

### API

- provedores intercambiáveis: Gemini, OpenAI e Anthropic Claude;
- análise de foto e texto preservando o contrato existente;
- campos descritivos de produtos tornados opcionais;
- pedidos demonstrativos com consentimento e retenção de 365 dias;
- token do navegador armazenado somente como hash;
- preço e disponibilidade recalculados no backend;
- limpeza periódica de registros expirados;
- importação de CSV/XLSX e organização de texto por IA;
- bloqueio das rotas administrativas na demonstração pública;
- diretório de dados configurável para o aplicativo desktop;
- logs com identificador e tempo das requisições de IA.

### Painel e distribuição

- importação em lote com prévia e política de duplicados;
- tela de pedidos demonstrativos;
- configuração local de provedor, modelo e chave de IA;
- remoção segura de imagens novas quando um cadastro falha;
- painel Tauri 2 com API FastAPI empacotada via PyInstaller;
- banco vazio e dados isolados por instalação;
- script local e workflow manual para gerar instalador Windows;
- divisão de bundles do painel para reduzir o arquivo inicial.

### Compatibilidade

- o marco `v3.9.0` permanece como versão final da V3;
- rotas anteriores de análise, catálogo e recomendação foram preservadas;
- o frontend Lumina continua sendo uma demonstração opcional da API.
