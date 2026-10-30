import streamlit as st
from chapters import CATEGORIES, CHAPTERS, DEADLINES

st.set_page_config(page_title="K-뷰티·K-푸드 수출 가이드", page_icon="📦", layout="wide")

# ---------------------------------------------------------------- 상단 눈에 띄는 헤더 디자인
st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a, #2563eb); padding: 1.8rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <h1 style="margin: 0; font-size: 1.9rem; font-weight: 700;">📦 K-뷰티·K-푸드 해외영업·수출마케팅 가이드</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
            일본 · 미국 · 동남아 · 유럽 | 기준일: 2026.10.29 | 규제와 관세는 수시로 변경되니 거래 전 반드시 최신 내용을 확인하세요.
        </p>
    </div>
""", unsafe_allow_html=True)

tab_guide, tab_price, tab_landed = st.tabs(["📖 가이드", "💰 역산 가격 계산기", "🚢 도착 원가 시뮬레이터"])

# ---------------------------------------------------------------- 가이드 탭
with tab_guide:
    st.warning("⚠️ **지금 확인해야 할 주요 시한**\n\n" + "\n".join(f"- {d}" for d in DEADLINES))

    st.markdown("#### 🗂️ 카테고리 분류 선택")
    all_cats = ["전체"] + list(CATEGORIES.values())
    cat = st.radio("분류 선택", all_cats, horizontal=True, label_visibility="collapsed")
    
    st.markdown("---")
    q = st.text_input("🔍 검색", placeholder="예: 할랄, MoCRA, FOB, 통관 등 키워드를 입력하세요.")

    # 필터링된 챕터 추출
    filtered_chapters = []
    for ch in CHAPTERS:
        if cat != "전체" and CATEGORIES[ch["cat"]] != cat:
            continue
        text = ch["title"] + ch["summary"] + " ".join(ch["points"])
        if q and q.lower() not in text.lower():
            continue
        filtered_chapters.append(ch)

    # 3열(Columns) 그리드 구조로 챕터 배치 및 제목 뒤 (a) 제거 적용
    cols = st.columns(3)
    for idx, ch in enumerate(filtered_chapters):
        with cols[idx % 3]:
            # 제목 뒤의 (a) 문자열 깔끔하게 제거
            clean_title = ch['title'].replace(" (a)", "").replace("(a)", "").strip()
            with st.expander(f"제 {ch['no']}장. {clean_title}"):
                st.write(ch["summary"])
                for p in ch["points"]:
                    st.markdown(f"- {p}")
                st.caption("💡 표, 템플릿 및 상세 문서는 버전을 참고하세요.")

# ---------------------------------------------------------------- 역산 가격 계산기 탭
with tab_price:
    st.subheader("💰 역산 가격 계산기")
    st.write("현지 소비자가에서 거꾸로 계산해 우리가 받을 수 있는 FOB 가격을 확인합니다. (마진은 판매가 기준)")

    c1, c2, c3 = st.columns(3)
    with c1:
        retail = st.number_input("현지 소비자가 (세금 제외, USD)", min_value=0.0, value=20.0, step=0.5)
        r_margin = st.slider("리테일러 마진 (%)", 0, 80, 40)
    with c2:
        d_margin = st.slider("총판 마진 (%)", 0, 60, 20)
        duty = st.number_input("수입 관세율 (%)", min_value=0.0, value=12.5, step=0.5)
    with c3:
        other = st.number_input("개당 물류·등록·기타 비용 (USD)", min_value=0.0, value=0.5, step=0.1)
        our_cost = st.number_input("우리 FOB 원가 (제조원가+관리비, USD)", min_value=0.0, value=5.0, step=0.1)

    retailer_buy = retail * (1 - r_margin / 100)
    dist_buy = retailer_buy * (1 - d_margin / 100)
    fob_max = max((dist_buy - other) / (1 + duty / 100), 0.0)
    margin = (fob_max - our_cost) / fob_max * 100 if fob_max > 0 else 0.0

    st.markdown("---")
    st.markdown("#### 📊 계산 결과 요약")
    m1, m2, m3 = st.columns(3)
    m1.metric("리테일러 매입가", f"${retailer_buy:,.2f}")
    m2.metric("총판 매입가", f"${dist_buy:,.2f}")
    m3.metric("수출 가능 FOB 상한", f"${fob_max:,.2f}")
    
    st.metric("💡 이 가격으로 판매 시 우리 마진", f"{margin:,.1f}%")
    if fob_max > 0 and margin < 0:
        st.error("🚨 원가가 FOB 상한보다 높습니다. 소비자가 인상, 용량·구성 변경, 또는 비용 조정이 필요합니다.")
    st.caption("※ 관세율은 FOB에 비례한다고 가정한 단순 계산입니다. 실제 관세 및 부수 비용은 관세사와 반드시 확인하세요.")

# ---------------------------------------------------------------- 도착 원가 시뮬레이터 탭
with tab_landed:
    st.subheader("🚢 도착 원가 시뮬레이터")
    st.write("바이어 입장에서 제품이 최종 도착했을 때의 개당 원가를 계산해 견적 경쟁력을 점검합니다.")

    c1, c2, c3 = st.columns(3)
    with c1:
        fob = st.number_input("FOB 단가 (USD)", min_value=0.0, value=8.0, step=0.1)
        qty = st.number_input("수량 (개)", min_value=1, value=5000, step=100)
    with c2:
        freight = st.number_input("국제 운임 총액 (USD)", min_value=0.0, value=1500.0, step=100.0)
        insurance = st.number_input("보험료 총액 (USD)", min_value=0.0, value=100.0, step=10.0)
    with c3:
        basis = st.radio("과세가격 기준", ["FOB 기준 (미국 등)", "CIF 기준 (EU·일본 등)"],
                         help="국가별로 과세 기준이 다릅니다.")
        duty2 = st.number_input("적용 관세율 (%)", min_value=0.0, value=12.5, step=0.5, key="duty2")
        local = st.number_input("현지 통관·내륙 운송·창고 총액 (USD)", min_value=0.0, value=800.0, step=50.0)

    goods = fob * qty
    cif = goods + freight + insurance
    base = goods if basis.startswith("FOB") else cif
    duty_amt = base * duty2 / 100
    total = cif + duty_amt + local

    st.markdown("---")
    st.markdown("#### 📊 도착 원가 분석 결과")
    m1, m2, m3 = st.columns(3)
    m1.metric("CIF 총액", f"${cif:,.0f}")
    m2.metric("관세", f"${duty_amt:,.0f}")
    m3.metric("도착 총원가", f"${total:,.0f}")
    
    st.metric("📦 개당 최종 도착 원가", f"${total / qty:,.2f}")
    st.caption("※ 미국 관세 구조는 최근 변동성이 큽니다(기본 한국 관세 구조 및 추가 조사 사항 반영). 정식 견적 전 현지 규정을 재확인하세요.")
