import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI 해외 마케팅 및 바이어 발굴 어드바이저", layout="wide")

st.title("🌐 AI 기반 해외 시장 분석 및 바이어 발굴 자동화")
st.markdown("수출할 제품 정보와 타겟 국가를 입력하면, AI가 타겟 바이어 프로필을 분석하고 맞춤형 영문 콜드메일 초안을 작성합니다.")

# 1. 기존에 시크릿에 등록하신 이름(MONOGPT_) 그대로 불러오기
client = OpenAI(
    base_url=st.secrets["MONOGPT_BASE_URL"],
    api_key=st.secrets["MONOGPT_API_KEY"]
)
MODEL_NAME = "gpt-6-luna"

# (이하 탭 레이아웃 및 분석/메일 생성 로직 코드는 그대로 유지)

# 2. 화면 레이아웃 구성
tab1, tab2 = st.tabs(["🎯 바이어 타겟팅 & 전략 분석", "✉️ 맞춤형 영문 콜드메일 생성"])

with tab1:
    st.subheader("🎯 해외 바이어 페르소나 및 시장 분석")
    
    with st.form("market_form"):
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("수출 제품명 (또는 카테고리)", placeholder="예: 프리미엄 기능성 화장품 / 제약 원료")
            target_country = st.text_input("타겟 국가", placeholder="예: 인도, 베트남, 독일 등")
        with col2:
            buyer_type = st.selectbox("타겟 바이어 유형", ["현지 총판 디스트리뷰터 (Distributor)", "대형 수입/유통사 (Importer)", "B2B 이커머스 셀러", "현지 제조사 (OEM 파트너)"])
            key_strength = st.text_input("제품 차별점 / 강점", placeholder="예: 우수한 가성비, 독자 성분 보유, 할랄 인증 완료")
            
        submitted_market = st.form_submit_button("🚀 바이어 발굴 전략 분석 실행")
        
        if submitted_market:
            with st.spinner("AI가 글로벌 시장 트렌드와 타겟 바이어 성향을 분석 중입니다..."):
                prompt = (
                    f"다음 제품의 해외 마케팅 및 바이어 발굴 전략을 세워줘:\n"
                    f"- 제품명: {item_name}\n"
                    f"- 타겟 국가: {target_country}\n"
                    f"- 타겟 바이어: {buyer_type}\n"
                    f"- 제품 강점: {key_strength}\n\n"
                    f"1. 해당 국가의 현지 시장 동향 및 수요 분석\n"
                    f"2. 이상적인 바이어 프로필 (어떤 기업을 타겟해야 하는지)\n"
                    f"3. 바이어를 찾을 수 있는 주요 채널 및 플랫폼 (예: B2B 플랫폼, 현지 전시회 등)\n"
                    f"4. 바이어 접근 핵심 전략을 구조화해서 작성해 줘."
                )
                
                try:
                    # 엘리스 모델은 temperature를 지원하지 않거나 기본값(1)만 지원하므로 매개변수 제거
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": "너는 글로벌 무역 마케팅 전문가이자 B2B 해외 영업 디렉터야."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    st.success("시장 분석 및 바이어 발굴 전략이 수립되었습니다!")
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")

with tab2:
    st.subheader("✉️ 바이어 맞춤형 영문 콜드메일(Cold Mail) 자동 생성")
    st.markdown("발견한 바이어에게 보낼 매력적인 첫인상 메일 초안을 자동으로 작성합니다.")
    
    with st.form("mail_form"):
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("우리회사 명칭", placeholder="예: KJ H&B")
            buyer_company = st.text_input("바이어 회사명", placeholder="예: Apex Pharma India")
        with col2:
            product_detail = st.text_input("제안 품목 핵심 내용", placeholder="예: 더마 코스메틱 수분크림 라인업")
            tone_manner = st.selectbox("톤앤매너", ["전문적이고 격식 있는 (Formal)", "친근하고 설득력 있는 (Persuasive)", "간결하고 핵심 위주 (Concise)"])
            
        submitted_mail = st.form_submit_button("✨ 영문 제안 메일 생성하기")
        
        if submitted_mail:
            with st.spinner("바이어의 마음을 사로잡을 영문 아웃바운드 메일을 작성 중입니다..."):
                mail_prompt = (
                    f"다음 조건에 맞춰 해외 바이어에게 보낼 영문 콜드메일(Cold Mail) 초안을 작성해 줘:\n"
                    f"- 발신 기업: {company_name}\n"
                    f"- 수신 바이어 기업: {buyer_company}\n"
                    f"- 제안 제품: {product_detail}\n"
                    f"- 톤앤매너: {tone_manner}\n\n"
                    f"조건:\n"
                    f"1. 제목(Subject)은 바이어가 열어보고 싶도록 매력적이고 직관적으로 3가지 옵션을 제시할 것.\n"
                    f"2. 본문은 바이어가 얻을 수 있는 비즈니스 가치(이익, 차별성) 중심으로 작성할 것.\n"
                    f"3. 콜 투 액션(CTA, 미팅 제안 등)을 명확히 포함할 것."
                )
                
                try:
                    # 스트리밍 응답에서도 temperature 매개변수 제거
                    stream_response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": "너는 글로벌 수출 영업 20년 경력의 수석 매니저야. 바이어 응답률이 높은 전문 비즈니스 영문 메일을 작성해."},
                            {"role": "user", "content": mail_prompt}
                        ],
                        stream=True
                    )
                    st.success("영문 콜드메일 초안이 완성되었습니다!")
                    st.write_stream(stream_response)
                except Exception as e:
                    st.error(f"메일 생성 중 오류 발생: {e}")
