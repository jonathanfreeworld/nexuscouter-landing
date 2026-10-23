import openai
import streamlit as st

# Streamlit secrets에서 API 키 불러오기
openai_api_key = st.secrets.get("OPENAI_API_KEY", "")

st.markdown("### 🎯 해외 바이어 페르소나 및 시장 분석")

# ... (입력창 코드들 동일) ...

if st.button("🚀 바이어 발굴 전략 분석 실행", key="btn_strategy"):
  if product_name and target_country:
    if not openai_api_key:
      st.error(
          "OpenAI API 키가 설정되지 않았습니다. Streamlit Secrets를 확인해"
          " 주세요."
      )
    else:
      with st.spinner("AI가 타겟 시장과 페르소나를 심층 분석 중입니다..."):
        try:
          # OpenAI 클라이언트 초기화
          client = openai.OpenAI(api_key=openai_api_key)

          # GPT에 전달할 프롬프트 작성
          prompt = f"""
                    당신은 글로벌 B2B 수출 및 무역 전문 AI 어드바이저입니다.
                    다음 조건에 맞춰 전문적이고 구체적인 바이어 타겟팅 및 진출 전략 리포트를 작성해 주세요.
                    
                    - 수출 제품명: {product_name}
                    - 타겟 국가: {target_country}
                    - 타겟 바이어 유형: {target_type}
                    - 제품 강점: {product_strength}
                    
                    리포트는 마크다운 형식으로 작성하고, 현지 시장 특성, 규제 고려사항, 구체적인 바이어 발굴 채널 및 액션 플랜을 상세히 포함해 주세요.
                    """

          response = client.chat.completions.create(
              model="gpt-4o",  # 또는 gpt-3.5-turbo
              messages=[{"role": "user", "content": prompt}],
              temperature=0.7,
          )

          strategy_result = response.choices[0].message.content

          st.success("심층 분석이 완료되었습니다!")
          st.markdown(strategy_result)

        except Exception as e:
          st.error(f"API 호출 중 오류가 발생했습니다: {e}")
  else:
    st.warning("수출 제품명과 타겟 국가를 입력해 주세요.")
