const DEFAULT_API_URL = 'http://127.0.0.1:8000';
const API_STORAGE_KEY = 'analise-pele:example-api-url';

const apiInput = document.querySelector('#api-url');
const connectionMessage = document.querySelector('#connection-message');
const statusDot = document.querySelector('.status-dot');
const resultPanel = document.querySelector('.result-panel');
const resultEmpty = document.querySelector('#result-empty');
const loading = document.querySelector('#loading');
const result = document.querySelector('#result');
const forms = [...document.querySelectorAll('.analysis-form')];

function normalizeApiUrl(value) {
  return (value || DEFAULT_API_URL).trim().replace(/\/$/, '');
}

apiInput.value = normalizeApiUrl(localStorage.getItem(API_STORAGE_KEY));

document.querySelector('#save-api').addEventListener('click', () => {
  apiInput.value = normalizeApiUrl(apiInput.value);
  localStorage.setItem(API_STORAGE_KEY, apiInput.value);
  connectionMessage.textContent = 'Endereço salvo neste navegador.';
});

if (window.location.protocol === 'file:') {
  document.querySelector('#file-alert').hidden = false;
}

document.querySelectorAll('.mode').forEach((button) => {
  button.addEventListener('click', () => {
    const selected = button.dataset.panel;
    document.querySelectorAll('.mode').forEach((item) => {
      item.classList.toggle('active', item === button);
    });
    forms.forEach((form) => {
      const active = form.dataset.form === selected;
      form.classList.toggle('active', active);
      form.hidden = !active;
    });
  });
});

async function readResponse(response) {
  let payload;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const detail = payload?.detail;
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map((item) => item.msg).join(' • ')
        : payload?.message || `A API respondeu com HTTP ${response.status}.`;
    throw new Error(message);
  }
  return payload;
}

async function apiRequest(path, options = {}, timeoutMs = 90000) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  const apiUrl = normalizeApiUrl(apiInput.value);
  try {
    const response = await fetch(`${apiUrl}${path}`, {
      ...options,
      signal: controller.signal,
    });
    return await readResponse(response);
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('A API demorou mais de 90 segundos. Verifique o servidor e tente novamente.');
    }
    if (error instanceof TypeError) {
      throw new Error('Não foi possível alcançar a API. Confira endereço, CORS, HTTPS e se o backend está ligado.');
    }
    throw error;
  } finally {
    window.clearTimeout(timer);
  }
}

document.querySelector('#test-status').addEventListener('click', async () => {
  statusDot.className = 'status-dot';
  connectionMessage.textContent = 'Testando conexão…';
  try {
    const data = await apiRequest('/status', {}, 15000);
    statusDot.classList.add('ok');
    connectionMessage.textContent = `Conectado: ${data.projeto || data.status || 'API disponível'}`;
  } catch (error) {
    statusDot.classList.add('fail');
    connectionMessage.textContent = error.message;
  }
});

function setLoading(active) {
  resultPanel.setAttribute('aria-busy', String(active));
  loading.hidden = !active;
  resultEmpty.hidden = true;
  result.hidden = true;
  forms.forEach((form) => {
    const submit = form.querySelector('[type="submit"]');
    submit.disabled = active;
  });
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function absoluteImageUrl(path) {
  if (!path) return '';
  if (/^https?:\/\//i.test(path)) return path;
  return `${normalizeApiUrl(apiInput.value)}${path.startsWith('/') ? '' : '/'}${path}`;
}

function flattenRecommendations(groups = {}) {
  return Object.entries(groups).flatMap(([category, products]) =>
    (products || []).map((product) => ({ ...product, categoryLabel: category }))
  );
}

function renderError(message) {
  setLoading(false);
  result.hidden = false;
  result.replaceChildren();
  const card = element('div', 'error-card');
  card.append(element('strong', '', 'Não foi possível concluir'));
  card.append(element('p', '', message));
  result.append(card);
}

function renderData(data) {
  setLoading(false);
  result.hidden = false;
  result.replaceChildren();

  result.append(element('span', 'result-label', data.status || 'Resposta recebida'));

  if (['informacoes_insuficientes', 'fora_escopo', 'imagem_inadequada', 'confirmacao_necessaria'].includes(data.status)) {
    result.append(element('h2', 'result-title', 'A análise precisa de mais uma etapa.'));
    result.append(element('p', 'result-message', data.mensagem || 'Confira as informações retornadas pela API.'));
  } else {
    result.append(element('h2', 'result-title', 'Perfil e recomendações recebidos.'));
    result.append(element('p', 'result-message', 'Agora seu frontend decide como apresentar esse conteúdo.'));
  }

  const profile = data.perfil;
  if (profile) {
    const chips = element('div', 'profile-chips');
    if (profile.tipo_pele) chips.append(element('span', 'chip', `Pele ${profile.tipo_pele}`));
    if (profile.sensivel !== null && profile.sensivel !== undefined) chips.append(element('span', 'chip', profile.sensivel ? 'Sensível' : 'Não sensível'));
    if (profile.tem_espinha !== null && profile.tem_espinha !== undefined) chips.append(element('span', 'chip', profile.tem_espinha ? 'Com espinhas' : 'Sem espinhas informadas'));
    result.append(chips);
  }

  const products = flattenRecommendations(data.recomendacoes).slice(0, 5);
  if (products.length) {
    result.append(element('p', 'result-label', `${data.total_recomendacoes ?? products.length} produtos compatíveis`));
    const list = element('div', 'products');
    products.forEach((product) => {
      const card = element('article', 'product');
      const imageUrl = absoluteImageUrl(product.imagem_url);
      if (imageUrl) {
        const image = element('img', 'product-image');
        image.src = imageUrl;
        image.alt = product.nome;
        image.loading = 'lazy';
        image.addEventListener('error', () => image.replaceWith(element('span', 'product-placeholder', product.nome?.[0] || '?')));
        card.append(image);
      } else {
        card.append(element('span', 'product-placeholder', product.nome?.[0] || '?'));
      }
      const description = element('div');
      description.append(element('strong', '', product.nome || 'Produto sem nome'));
      description.append(element('small', '', `${product.marca || 'Marca não informada'} • ${product.categoryLabel}`));
      card.append(description);
      card.append(element('span', 'product-price', Number(product.preco || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })));
      list.append(card);
    });
    result.append(list);
  }

  const details = element('details', 'raw');
  details.append(element('summary', '', 'Ver JSON completo'));
  details.append(element('pre', '', JSON.stringify(data, null, 2)));
  result.append(details);
}

document.querySelector('#form-manual').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  setLoading(true);
  try {
    const data = await apiRequest('/recomendacoes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tipo_pele: form.get('tipo_pele'),
        sensivel: form.has('sensivel'),
        tem_espinha: form.has('tem_espinha'),
      }),
    });
    renderData(data);
  } catch (error) {
    renderError(error.message);
  }
});

document.querySelector('#form-texto').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  setLoading(true);
  try {
    const data = await apiRequest('/analise-texto', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texto: form.get('texto') }),
    });
    renderData(data);
  } catch (error) {
    renderError(error.message);
  }
});

document.querySelector('#form-foto').addEventListener('submit', async (event) => {
  event.preventDefault();
  const source = new FormData(event.currentTarget);
  const file = source.get('arquivo');
  if (!(file instanceof File) || !file.size) {
    renderError('Escolha uma imagem antes de continuar.');
    return;
  }
  const body = new FormData();
  body.append('arquivo', file);
  const text = String(source.get('texto') || '').trim();
  if (text) body.append('texto', text);

  setLoading(true);
  try {
    const data = await apiRequest('/analise-foto', { method: 'POST', body });
    renderData(data);
  } catch (error) {
    renderError(error.message);
  }
});
