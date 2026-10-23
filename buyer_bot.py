import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="nexuscouter | AI 어드바이저",
    page_icon="🌐",
    layout="wide",
)

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

  # 안전한 2열 컬럼 설정
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
        placeholder="예: 우수한 가성비, 독자 성분 보유, 할랄 인증 완료",
        key="t1_strength",
    )

  st.write("")
  if st.button("🚀 바이어 발굴 전략 분석 실행", key="btn_strategy"):
    if product_name and target_country:
      with st.spinner("AI가 타겟 시장과 페르소나를 분석 중입니다..."):
        strategy_result = f"""
                ---
                ### 📊 [{target_country}] 바이어 타겟팅 및 진출 전략 결과
                
                - **분석 대상 제품**: {product_name}
                - **타겟 바이어 유형**: {target_type}
                - **제품 주요 강점**: {product_strength if product_strength else "입력된 강점 없음"}
                
                #### 💡 핵심 진출 전략
                1. **현지 파트너 발굴 방향**: {target_country} 내에서 해당 카테고리 유통 경험이 풍부한 {target_type}를 우선 타겟팅합니다.
                2. **마케팅 소통 포인트**: 제품의 차별점과 현지 규격 적합성을 강조하여 신뢰도를 높입니다.
                3. **추천 액션 플랜**: 초도 물량은 소량 테스트 오더 방식으로 진입하여 바이어의 리스크를 줄여주는 방안을 제안합니다.
                """

        st.success("분석이 완료되었습니다!")
        st.markdown(strategy_result)
    else:
      st.warning("수출 제품명과 타겟 국가를 입력해 주세요.")

# 2. 맞춤형 영문 콜드메일 생성 탭
with tab2:
  st.markdown("### ✉️ 바이오 맞춤형 영문 콜드메일(Cold Mail) 자동 생성")
  st.write(
      "발견한 바이어에게 보낼 매력적인 첫인상 메일 초안을 자동으로"
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
        placeholder="예: 더마 코스메틱 수분크림 라인업",
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
      with st.spinner("맞춤형 영문 콜드메일을 작성 중입니다..."):
        mail_result = f"""
                ---
                ### 📝 생성된 영문 콜드메일 초안 ({tone_manner})
                
                **Subject:** Partnership Proposal: Premium {item_content} from {company_name}
                
                Dear {buyer_name} Team,
                
                I hope this email finds you well. 
                My name is from {company_name}, and we specialize in high-quality {item_content}.
                
                We have been following {buyer_name}'s remarkable presence in the market and believe our innovative product line would be an exceptional fit for your portfolio.
                
                **Key Highlights:**
                - Premium quality tailored for global standards.
                - Highly competitive partnership terms.
                
                We would love to share product samples and discuss a potential collaboration. Could we schedule a brief call next week?
                
                Best regards,
                {company_name} Export Team
                """

        st.success("콜드메일 초안이 생성되었습니다!")
        st.markdown(mail_result)
    else:
      st.warning("필수 입력 항목을 모두 작성해 주세요.")
