# Changelog

## 4.0.0

### Arquitetura

- removida a tentativa de distribuição por Tauri, PyInstaller e sidecar;
- removidos o instalador Windows, o ambiente `desktop`, a porta 8765 e o workflow correspondente;
- Skin Admin consolidado como painel web que consome `VITE_API_URL`;
- configuração de chaves e modelos de IA mantida exclusivamente no backend;
- versão da API normalizada como `4.0.0`.

### API e experiência

- provedores intercambiáveis: Gemini, OpenAI e Anthropic Claude;
- análise por foto, texto ou perfil direto;
- recomendação determinística;
- catálogo com imagens, importação CSV/XLSX/IA e política de duplicados;
- pedidos demonstrativos identificados por cliente, com consentimento e retenção;
- preço e disponibilidade recalculados no backend;
- rotas administrativas bloqueadas no ambiente de produção sem autenticação.

### Compatibilidade

- o marco `v3.9.0` permanece como versão final da V3;
- as rotas públicas anteriores de análise, catálogo e recomendação foram preservadas;
- o frontend Lumina continua sendo uma demonstração opcional da API.
