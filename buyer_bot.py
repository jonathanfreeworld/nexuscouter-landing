import streamlit as st

# 페이지 설정 (기존 설정 유지)
st.set_page_config(page_title="nexuscouter AI Advisor", layout="wide")

# 탭 또는 네비게이션 구조 예시
tab1, tab2 = st.tabs(
    ["🎯 바이어 타겟팅 & 전략 분석", "✉️ 맞춤형 영문 콜드메일 생성"]
)

with tab1:
  st.markdown("### 🎯 해외 바이어 페르소나 및 시장 분석")
  st.write("해외 진출을 위한 타겟 시장과 바이어 조건을 설정하세요.")

  # 좌우 2열(2칸)로 입력 필드 배치
  col1, col2 = st.columns(2)

  with col1:
    product_name = st.text_input(
        "수출 제품명 (또는 카테고리)",
        placeholder="예: 프리미엄 기능성 화장품 / 제약 원료",
    )
    target_type = st.selectbox(
        "타겟 바이어 유형",
        [
            "현지 총판 디스트리뷰터 (Distributor)",
            "수입사 / 도매상 (Importer / Wholesaler)",
            "현지 온·오프라인 리테일러",
            "기타 파트너",
        ],
    )

  with col2:
    target_country = st.text_input(
        "타겟 국가", placeholder="예: 인도, 베트남, 독일 등"
    )
    product_strength = st.text_input(
        "제품 차별점 / 강점",
        placeholder="예: 우수한 가성비, 독자 성분 보유, 할랄 인증 완료",
    )

  # 실행 버튼
  if st.button("🚀 바이어 발굴 전략 분석 실행"):
    if product_name and target_country:
      with st.spinner("AI가 타겟 시장과 바이어 페르소나를 분석 중입니다..."):
        # 여기에 분석 결과 출력 로직 작성
        st.success("분석이 완료되었습니다!")
    else:
      st.warning("수출 제품명과 타겟 국가를 입력해 주세요.")

with tab2:
  # 기존 콜드메일 생성 화면 코드
  st.markdown("### ✉️ 바이오 맞춤형 영문 콜드메일(Cold Mail) 자동 생성")
  # (콜드메일 관련 기존 코드 유지)
