import openai
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="nexuscouter | AI 어드바이저",
    page_icon="🌐",
    layout="wide",
)

# Streamlit Secrets에서 설정값 안전하게 불러오기
try:
  API_BASE_URL = st.secrets["API_BASE_URL"]
  API_KEY = st.secrets["API_KEY"]
  MODEL_NAME = st.secrets.get("MODEL_NAME", "gpt-6-luna")
except Exception:
  API_BASE_URL = ""
  API_KEY = ""
  MODEL_NAME = "gpt-6-luna"

# 상단 탭 메뉴 구성
tab1, tab2 = st.tabs(
    ["🎯 바이어 타겟팅 & 전략 분석", "✉️ 맞춤형 영문 콜드메일 생성"]
)

# 1. 바이어 타겟팅 & 전략 분석 탭
with tab1:
  st.markdown("### 🎯 해외 바이어 페르소나 및 시장 분석")
  st.write(
      "해외 진출을 위한 타겟 시장과 바이어 조건을 설정하여 맞춤형 전략을"
      " 확인하세요."
  )

  col1, col2 = st.columns(2)

  with col1:
    product_name = st.text_input(
        "수출 제품명 (또는 카테고리)",
        placeholder="예: 프리미엄 기능성 화장품 / 제약 원료",
        key="t1_product",
    )
    target_type = st.selectbox(
        "타겟 바이어 유형",
        [
            "현지 총판 디스트리뷰터 (Distributor)",
            "수입사 / 도매상 (Importer / Wholesaler)",
            "현지 온·오프라인 리테일러",
            "기타 파트너",
        ],
        key="t1_type",
    )

  with col2:
    target_country = st.text_input(
        "타겟 국가",
        placeholder="예: 인도, 베트남, 독일 등",
        key="t1_country",
    )
    product_strength = st.text_input(
        "제품 차별점 / 강점",
        placeholder="예: 칼라테라피, 미백, 주름개선, 식물성 추출원료",
        key="t1_strength",
    )

  st.write("")
  if st.button("🚀 바이어 발굴 전략 분석 실행", key="btn_strategy"):
    if product_name and target_country:
      if not API_KEY or not API_BASE_URL:
        st.error(
            "⚠️ Streamlit Secrets에 API 설정(API_BASE_URL, API_KEY)이"
            " 누락되었습니다."
        )
      else:
        with st.spinner(f"[{target_country}] 진출 전략을 생성 중입니다..."):
          try:
            client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

            # 불필요한 장문 유도 프롬프트를 간소화하여 토큰 소모를 방지합니다.
            prompt = f"""
                        수출 제품명: {product_name}
                        타겟 국가: {target_country}
                        타겟 바이어 유형: {target_type}
                        제품 강점: {product_strength}
                        
                        위 조건에 맞는 바이어 타겟팅 및 수출 진출 전략을 마크다운 형식으로 핵심 위주로 간결하게 작성해 주세요.
                        """

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=1000,
            )

            strategy_result = None
            if response.choices and len(response.choices) > 0:
              msg = response.choices[0].message
              if hasattr(msg, "content") and msg.content:
                strategy_result = msg.content
              elif isinstance(msg, dict) and "content" in msg:
                strategy_result = msg["content"]

            if strategy_result:
              st.success("전략 분석이 완료되었습니다!")
              st.markdown("---")
              st.markdown(strategy_result)
            else:
              st.warning("결과를 불러오지 못했습니다. 다시 시도해 주세요.")

          except Exception as e:
            st.error(f"API 호출 중 오류가 발생했습니다: {e}")
    else:
      st.warning("수출 제품명과 타겟 국가를 입력해 주세요.")

# 2. 맞춤형 영문 콜드메일 생성 탭
with tab2:
  st.markdown("### ✉️ 바이오 맞춤형 영문 콜드메일(Cold Mail) 자동 생성")
  st.write(
      "발견한 바이어에게 보낼 매력적인 첫인상 영문 메일 초안을 자동으로"
      " 작성합니다."
  )

  col3, col4 = st.columns(2)

  with col3:
    company_name = st.text_input(
        "우리회사 명칭", placeholder="예: KJ H&B", key="t2_company"
    )
    buyer_name = st.text_input(
        "바이어 회사명",
        placeholder="예: Apex Pharma India",
        key="t2_buyer",
    )

  with col4:
    item_content = st.text_input(
        "제안 품목 핵심 내용",
        placeholder="예: 기능성 화장품 및 식물성 추출원료",
        key="t2_item",
    )
    tone_manner = st.selectbox(
        "톤앤매너",
        [
            "전문적이고 격식 있는 (Formal)",
            "친근하고 설득력 있는 (Friendly & Persuasive)",
            "간결하고 명확한 (Concise & Direct)",
        ],
        key="t2_tone",
    )

  st.write("")
  if st.button("✨ 영문 제안 메일 생성하기", key="btn_mail"):
    if company_name and buyer_name and item_content:
      if not API_KEY or not API_BASE_URL:
        st.error(
            "⚠️ Streamlit Secrets에 API 설정(API_BASE_URL, API_KEY)이"
            " 누락되었습니다."
        )
      else:
        with st.spinner("영문 콜드메일 초안을 작성 중입니다..."):
          try:
            client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
            mail_prompt = f"""
                        보내는 회사: {company_name}
                        수신 바이어 회사: {buyer_name}
                        제안 품목: {item_content}
                        톤앤매너: {tone_manner}
                        
                        위 정보를 바탕으로 바이어에게 보낼 영문 콜드메일 초안을 작성해 주세요. (Subject, 본문 포함)
                        """

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": mail_prompt}],
                max_completion_tokens=1000,
            )

            mail_result = None
            if response.choices and len(response.choices) > 0:
              msg = response.choices[0].message
              if hasattr(msg, "content") and msg.content:
                mail_result = msg.content
              elif isinstance(msg, dict) and "content" in msg:
                mail_result = msg["content"]

            if mail_result:
              st.success("콜드메일 초안이 생성되었습니다!")
              st.markdown("---")
              st.markdown(mail_result)
            else:
              st.warning("결과를 불러오지 못했습니다. 다시 시도해 주세요.")

          except Exception as e:
            st.error(f"API 호출 중 오류가 발생했습니다: {e}")
    else:
      st.warning("필수 입력 항목을 모두 작성해 주세요.")
