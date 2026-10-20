(() => {
  'use strict';

  const header = document.querySelector('.site-header');
  const menuToggle = document.querySelector('.menu-toggle');
  const navLinks = document.querySelector('.nav-links');

  const setHeaderState = () => {
    if (header) header.classList.toggle('is-scrolled', window.scrollY > 24);
  };
  setHeaderState();
  window.addEventListener('scroll', setHeaderState, { passive: true });

  if (menuToggle && header) {
    menuToggle.addEventListener('click', () => {
      const isOpen = header.classList.toggle('menu-open');
      menuToggle.setAttribute('aria-expanded', String(isOpen));
    });
  }

  document.querySelectorAll('.nav-links a').forEach((link) => {
    link.addEventListener('click', () => {
      if (header) header.classList.remove('menu-open');
      if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
    });
  });

  document.querySelectorAll('.accordion-trigger').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const panelId = trigger.getAttribute('aria-controls');
      const panel = panelId ? document.getElementById(panelId) : null;
      const expanded = trigger.getAttribute('aria-expanded') === 'true';
      trigger.setAttribute('aria-expanded', String(!expanded));
      if (panel) panel.classList.toggle('is-open', !expanded);
    });
  });

  const planSelect = document.querySelector('[name="plan"]');
  document.querySelectorAll('[data-plan]').forEach((button) => {
    button.addEventListener('click', () => {
      const value = button.getAttribute('data-plan');
      if (planSelect && value) planSelect.value = value;
    });
  });

  const calcInputs = document.querySelectorAll('[data-cbm-input]');
  const calcOutput = document.querySelector('[data-cbm-output]');
  const calculateCbm = () => {
    if (!calcOutput || calcInputs.length < 4) return;
    const values = Array.from(calcInputs).map((input) => Math.max(0, Number(input.value) || 0));
    const cbm = (values[0] * values[1] * values[2] * values[3]) / 1000000000;
    calcOutput.textContent = `${cbm.toFixed(3)} CBM`;
  };
  calcInputs.forEach((input) => input.addEventListener('input', calculateCbm));
  calculateCbm();

  const form = document.querySelector('[data-contact-form]');
  if (form) {
    form.addEventListener('submit', (event) => {
      if (!form.checkValidity()) {
        event.preventDefault();
        const status = form.querySelector('.form-status');
        if (status) {
          status.textContent = '필수 항목을 확인해 주세요.';
          status.className = 'form-status is-error';
        }
        form.reportValidity();
        return;
      }
      const submit = form.querySelector('button[type="submit"]');
      if (submit) {
        submit.disabled = true;
        submit.textContent = '전송 준비 중…';
      }
    });
  }

  const status = document.querySelector('.form-status[data-auto-hide]');
  if (status) window.setTimeout(() => { status.textContent = ''; }, 8500);

  const revealElements = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const observer = new IntersectionObserver((entries, instance) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          instance.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealElements.forEach((element) => observer.observe(element));
  } else {
    revealElements.forEach((element) => element.classList.add('is-visible'));
  }
})();
