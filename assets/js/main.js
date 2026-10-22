(() => {
  'use strict';

  const header = document.querySelector('.site-header');
  const menuToggle = document.querySelector('.menu-toggle');
  const setHeaderState = () => { if (header) header.classList.toggle('is-scrolled', window.scrollY > 24); };
  setHeaderState();
  window.addEventListener('scroll', setHeaderState, { passive: true });
  if (menuToggle && header) {
    menuToggle.addEventListener('click', () => {
      const isOpen = header.classList.toggle('menu-open');
      menuToggle.setAttribute('aria-expanded', String(isOpen));
    });
  }
  document.querySelectorAll('.nav-links a').forEach((link) => link.addEventListener('click', () => {
    if (header) header.classList.remove('menu-open');
    if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
  }));
  document.querySelectorAll('.accordion-trigger').forEach((trigger) => trigger.addEventListener('click', () => {
    const panel = document.getElementById(trigger.getAttribute('aria-controls'));
    const expanded = trigger.getAttribute('aria-expanded') === 'true';
    trigger.setAttribute('aria-expanded', String(!expanded));
    if (panel) panel.classList.toggle('is-open', !expanded);
  }));
  const planSelect = document.querySelector('[name="plan"]');
  document.querySelectorAll('[data-plan]').forEach((button) => button.addEventListener('click', () => {
    if (planSelect) planSelect.value = button.getAttribute('data-plan') || '';
  }));

  const numberValue = (selector) => Math.max(0, Number(document.querySelector(selector)?.value) || 0);
  const formatNumber = (value) => new Intl.NumberFormat('ko-KR').format(Math.max(0, Math.floor(value)));

  // CBM is shown separately for reference only. Container loading never uses total CBM.
  const calcInputs = document.querySelectorAll('[data-cbm-input]');
  const calcOutput = document.querySelector('[data-cbm-output]');
  const calculateCbm = () => {
    if (!calcOutput || calcInputs.length < 4) return;
    const values = Array.from(calcInputs).map((input) => Math.max(0, Number(input.value) || 0));
    calcOutput.textContent = `${((values[0] * values[1] * values[2] * values[3]) / 1000000000).toFixed(3)} CBM`;
  };
  calcInputs.forEach((input) => input.addEventListener('input', calculateCbm));
  calculateCbm();

  const containerSpecs = [
    { key: '20', length: 5898, width: 2352, height: 2393 },
    { key: '40', length: 12032, width: 2352, height: 2393 },
    { key: '40hq', length: 12032, width: 2352, height: 2698 },
  ];

  const orientationCapacity = (length, width, itemLength, itemWidth) => {
    if (!length || !width || !itemLength || !itemWidth) return { count: 0, label: '-' };
    const normal = Math.floor(length / itemLength) * Math.floor(width / itemWidth);
    const rotated = Math.floor(length / itemWidth) * Math.floor(width / itemLength);
    return normal >= rotated
      ? { count: normal, label: `${itemLength} × ${itemWidth} 방향` }
      : { count: rotated, label: `${itemWidth} × ${itemLength} 방향` };
  };

  const calculatePalletPlan = () => {
    const palletL = numberValue('#pallet-length');
    const palletW = numberValue('#pallet-width');
    const palletH = numberValue('#pallet-height');
    const skuPlans = [1, 2, 3].map((sku) => {
      const boxL = numberValue(`#sku${sku}-length`);
      const boxW = numberValue(`#sku${sku}-width`);
      const boxH = numberValue(`#sku${sku}-height`);
      const quantity = numberValue(`#sku${sku}-quantity`);
      const floor = orientationCapacity(palletL, palletW, boxL, boxW);
      const layers = boxH > 0 ? Math.floor(palletH / boxH) : 0;
      const boxesPerPallet = floor.count * layers;
      const requiredPallets = boxesPerPallet > 0 && quantity > 0 ? Math.ceil(quantity / boxesPerPallet) : 0;
      const remainder = boxesPerPallet > 0 && quantity > 0 ? quantity % boxesPerPallet : 0;
      return { sku, quantity, boxesPerPallet, requiredPallets, remainder, floor, boxH };
    });
    const totalPallets = skuPlans.reduce((sum, plan) => sum + plan.requiredPallets, 0);
    const totalBoxes = skuPlans.reduce((sum, plan) => sum + plan.quantity, 0);
    const activeSkus = skuPlans.filter((plan) => plan.quantity > 0);

    skuPlans.forEach((plan) => {
      const boxesEl = document.querySelector(`[data-sku-boxes-per-pallet="${plan.sku}"]`);
      const palletsEl = document.querySelector(`[data-sku-pallets="${plan.sku}"]`);
      const orientationEl = document.querySelector(`[data-sku-orientation="${plan.sku}"]`);
      const remainderEl = document.querySelector(`[data-sku-remainder="${plan.sku}"]`);
      if (boxesEl) boxesEl.textContent = plan.boxesPerPallet ? `${formatNumber(plan.boxesPerPallet)} 박스` : '-';
      if (palletsEl) palletsEl.textContent = plan.requiredPallets ? `${formatNumber(plan.requiredPallets)} PLT` : '-';
      if (orientationEl) orientationEl.textContent = plan.floor.count ? `${plan.floor.label} · ${plan.boxH > 0 ? Math.floor(numberValue('#pallet-height') / plan.boxH) : 0}단 적재` : '치수 입력 필요';
      if (remainderEl) remainderEl.textContent = plan.remainder ? `잔여 ${formatNumber(plan.remainder)}박스` : (plan.quantity ? '파렛트 단위로 나누어짐' : '수량 미입력');
    });

    const totalPalletsEl = document.querySelector('[data-required-pallets]');
    const totalBoxesEls = document.querySelectorAll('[data-total-boxes]');
    if (totalPalletsEl) totalPalletsEl.textContent = `${formatNumber(totalPallets)} PLT`;
    totalBoxesEls.forEach((element) => { element.textContent = `${formatNumber(totalBoxes)} 박스`; });

    containerSpecs.forEach((spec) => {
      const palletSlots = orientationCapacity(spec.length, spec.width, palletL, palletW);
      const heightOk = palletH > 0 && palletH <= spec.height;
      const totalCapacityPallets = heightOk ? palletSlots.count : 0;
      const containersNeeded = totalCapacityPallets > 0 && totalPallets > 0 ? Math.ceil(totalPallets / totalCapacityPallets) : 0;
      const capacityEl = document.querySelector(`[data-container-capacity="${spec.key}"]`);
      const palletSlotsEl = document.querySelector(`[data-container-pallets="${spec.key}"]`);
      const neededEl = document.querySelector(`[data-container-needed="${spec.key}"]`);
      const fillEl = document.querySelector(`[data-container-fill="${spec.key}"]`);
      const noteEl = document.querySelector(`[data-container-note="${spec.key}"]`);
      const skuCapacityEl = document.querySelector(`[data-container-sku-capacity="${spec.key}"]`);
      const skuCapacity = activeSkus.map((plan) => `SKU ${plan.sku}: ${formatNumber(totalCapacityPallets * plan.boxesPerPallet)}박스`).join(' · ');
      if (capacityEl) capacityEl.textContent = totalCapacityPallets ? `${formatNumber(totalCapacityPallets)} PLT` : '-';
      if (palletSlotsEl) palletSlotsEl.textContent = totalCapacityPallets ? `${formatNumber(totalCapacityPallets)} PLT` : '-';
      if (neededEl) neededEl.textContent = containersNeeded ? `${formatNumber(containersNeeded)}대` : '-';
      if (fillEl) fillEl.textContent = totalCapacityPallets > 0 && totalPallets > 0 ? `${Math.min(100, (totalPallets / totalCapacityPallets) * 100).toFixed(0)}%` : '계산 불가';
      if (skuCapacityEl) skuCapacityEl.textContent = skuCapacity || 'SKU별 수량 입력 필요';
      if (noteEl) noteEl.textContent = !heightOk && palletH > 0 ? '팔레트 적재 높이가 내부 높이를 초과합니다.' : (totalPallets ? `파렛트 ${palletSlots.label} 배치 · CBM 합산 미사용` : 'SKU와 파렛트 치수를 입력해 주세요.');
    });
  };
  document.querySelectorAll('[data-container-input]').forEach((input) => input.addEventListener('input', calculatePalletPlan));
  calculatePalletPlan();

  const form = document.querySelector('[data-contact-form]');
  if (form) form.addEventListener('submit', (event) => {
    if (!form.checkValidity()) {
      event.preventDefault();
      const status = form.querySelector('.form-status');
      if (status) { status.textContent = '필수 항목을 확인해 주세요.'; status.className = 'form-status is-error'; }
      form.reportValidity();
      return;
    }
    const submit = form.querySelector('button[type="submit"]');
    if (submit) { submit.disabled = true; submit.textContent = '전송 준비 중…'; }
  });
  const status = document.querySelector('.form-status[data-auto-hide]');
  if (status) window.setTimeout(() => { status.textContent = ''; }, 8500);

  const revealElements = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const observer = new IntersectionObserver((entries, instance) => entries.forEach((entry) => {
      if (entry.isIntersecting) { entry.target.classList.add('is-visible'); instance.unobserve(entry.target); }
    }), { threshold: 0.12 });
    revealElements.forEach((element) => observer.observe(element));
  } else revealElements.forEach((element) => element.classList.add('is-visible'));
})();
