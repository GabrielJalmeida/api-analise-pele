(() => {
  const tutorialId = document.body.dataset.tutorial || 'tutorial';
  const storageKey = `analise-pele:${tutorialId}:checks`;
  const toast = document.querySelector('[data-toast]');
  let toastTimer;

  function notify(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove('show'), 2200);
  }

  function copyFallback(text) {
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    const copied = document.execCommand('copy');
    area.remove();
    return copied;
  }

  document.querySelectorAll('.code-block').forEach((block) => {
    const button = block.querySelector('.copy-button');
    const code = block.querySelector('pre code');
    if (!button || !code) return;

    button.addEventListener('click', async () => {
      const value = code.textContent.replace(/^\n|\n$/g, '');
      let copied = false;
      try {
        await navigator.clipboard.writeText(value);
        copied = true;
      } catch {
        copied = copyFallback(value);
      }

      if (copied) {
        button.textContent = 'Copiado';
        button.classList.add('copied');
        notify('Código copiado.');
        window.setTimeout(() => {
          button.textContent = 'Copiar';
          button.classList.remove('copied');
        }, 1500);
      } else {
        notify('Selecione o código e pressione Ctrl + C.');
      }
    });
  });

  const checkboxes = [...document.querySelectorAll('[data-check-id]')];
  const progressBar = document.querySelector('[data-check-progress]');
  const progressText = document.querySelector('[data-check-progress-text]');

  function loadChecks() {
    let saved = [];
    try {
      saved = JSON.parse(localStorage.getItem(storageKey) || '[]');
    } catch {
      saved = [];
    }
    checkboxes.forEach((box) => {
      box.checked = saved.includes(box.dataset.checkId);
    });
  }

  function updateCheckProgress() {
    const done = checkboxes.filter((box) => box.checked).length;
    const total = checkboxes.length;
    const percentage = total ? Math.round((done / total) * 100) : 0;
    if (progressBar) progressBar.style.width = `${percentage}%`;
    if (progressText) progressText.textContent = `${done} de ${total} etapas`;

    const selected = checkboxes
      .filter((box) => box.checked)
      .map((box) => box.dataset.checkId);
    try {
      localStorage.setItem(storageKey, JSON.stringify(selected));
    } catch {
      // O tutorial continua funcional se o navegador bloquear armazenamento local.
    }
  }

  loadChecks();
  updateCheckProgress();
  checkboxes.forEach((box) => box.addEventListener('change', updateCheckProgress));

  document.querySelectorAll('[data-reset-checks]').forEach((button) => {
    button.addEventListener('click', () => {
      checkboxes.forEach((box) => { box.checked = false; });
      updateCheckProgress();
      notify('Progresso reiniciado.');
    });
  });

  document.querySelectorAll('[data-print]').forEach((button) => {
    button.addEventListener('click', () => window.print());
  });

  const readingBar = document.querySelector('[data-reading-progress]');
  function updateReadingProgress() {
    if (!readingBar) return;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const percentage = max > 0 ? Math.min(100, (window.scrollY / max) * 100) : 100;
    readingBar.style.width = `${percentage}%`;
  }
  updateReadingProgress();
  window.addEventListener('scroll', updateReadingProgress, { passive: true });

  const sections = [...document.querySelectorAll('main section[id]')];
  const tocLinks = [...document.querySelectorAll('.toc a[href^="#"]')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      tocLinks.forEach((link) => {
        const active = link.getAttribute('href') === `#${visible.target.id}`;
        link.classList.toggle('active', active);
        if (active) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
    }, { rootMargin: '-18% 0px -70% 0px', threshold: [0, 0.2, 0.6] });
    sections.forEach((section) => observer.observe(section));
  }

  document.querySelectorAll('[data-tabs]').forEach((tabs) => {
    const buttons = [...tabs.querySelectorAll('[role="tab"]')];
    const panels = [...tabs.querySelectorAll('[role="tabpanel"]')];
    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        buttons.forEach((item) => item.setAttribute('aria-selected', String(item === button)));
        panels.forEach((panel) => {
          panel.hidden = panel.id !== button.getAttribute('aria-controls');
        });
      });
    });
  });

  document.querySelectorAll('a[href^="http"]').forEach((link) => {
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
  });
})();
