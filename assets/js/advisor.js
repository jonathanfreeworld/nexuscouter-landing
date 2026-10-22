(() => {
  const form = document.querySelector('#advisor-form');
  const result = document.querySelector('#advisor-result');
  if (!form || !result) return;
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const product = document.querySelector('#advisor-product').value.trim();
    const country = document.querySelector('#advisor-country').value.trim();
    const stage = document.querySelector('#advisor-stage').value;
    const goal = document.querySelector('#advisor-goal').value;
    if (!product || !country) return;
    const status = document.querySelector('#advisor-status');
    const isRegulated = /화장품|식품|건강|의료|뷰티|cosmetic|food/i.test(product);
    const firstAction = goal === '바이어 발굴' ? 'HS 코드와 구매 조건을 정리한 뒤 목표 국가의 유통·수입 바이어 후보를 비교하세요.' : goal === '첫 아웃리치 메시지' ? '제품 차별점과 바이어별 가설을 넣은 짧은 영문 메시지 2종을 먼저 준비하세요.' : goal === '규제·인증 확인' ? '제품 분류와 국가별 공식 규제·인증 요건을 먼저 확인해 판매 가능 범위를 좁히세요.' : '박스 규격·파렛트 적재·인코텀즈를 입력해 예상 원가와 최소 판매 조건을 계산하세요.';
    const checks = isRegulated ? ['제품 분류와 성분·원재료 자료 정리', `${country} 공식 규제·인증 요건 1차 확인`, '바이어 후보와 아웃리치 메시지 검토'] : ['제품·가격·MOQ·납기 자료 정리', `${country} 타깃 바이어 후보군 정의`, '바이어별 아웃리치 메시지와 후속 일정 설계'];
    result.innerHTML = `<p class="eyebrow">Recommendation · ${country}</p><h2>${product}의<br>다음 실행 순서</h2><div class="advisor-summary"><span>현재 단계</span><strong>${stage}</strong><span>우선 목표</span><strong>${goal}</strong></div><div class="advisor-priority"><b>우선 실행</b><p>${firstAction}</p></div><h3>확인할 항목</h3><ol class="advisor-checklist">${checks.map((item) => `<li>${item}</li>`).join('')}</ol><p class="calc-footnote">이 결과는 데모용 샘플 추천이며 법률·인증·통관 판단이나 실제 AI 분석 결과를 대체하지 않습니다.</p>`;
    if (status) { status.textContent = '추천 결과를 생성했습니다.'; status.className = 'form-status is-success'; }
  });
})();
