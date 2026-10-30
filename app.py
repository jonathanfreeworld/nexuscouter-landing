import streamlit as st
from chapters import CATEGORIES, CHAPTERS, DEADLINES

st.set_page_config(page_title="K-뷰티·K-푸드 수출 가이드", page_icon="📦", layout="wide")

st.title("K-뷰티·K-푸드 해외영업·수출마케팅 가이드")
st.caption("일본·미국·동남아·유럽 | 2026.10.29 기준 | 규제와 관세는 수시로 바뀝니다. 거래 전 최신 내용을 확인하세요.")

tab_guide, tab_price, tab_landed = st.tabs(["가이드", "역산 가격 계산기", "도착 원가 시뮬레이터"])

# ---------------------------------------------------------------- 가이드
with tab_guide:
    st.warning("**지금 확인해야 할 시한**\n\n" + "\n".join(f"- {d}" for d in DEADLINES))

    # 분류와 검색 영역을 컬럼으로 깔끔하게 배치하여 스크롤 최소화
    col_cat, col_search = st.columns([2, 3])
    
    all_cats = ["전체"] + list(CATEGORIES.values())
    
    with col_cat:
        cat = st.selectbox("분류 선택", all_cats)
    with col_search:
        q = st.text_input("검색", placeholder="예: 할랄, MoCRA, FOB")

    for ch in CHAPTERS:
        if cat != "전체" and CATEGORIES[ch["cat"]] != cat:
            continue
        text = ch["title"] + ch["summary"] + " ".join(ch["points"])
        if q and q.lower() not in text.lower():
            continue
        with st.expander(f"{ch['no']}장. {ch['title']}"):
            st.write(ch["summary"])
            for p in ch["points"]:
                st.markdown(f"- {p}")
            st.caption("표, 템플릿, 확인이 필요한 항목은 문서 버전에 있습니다.")

# ---------------------------------------------------------------- 역산 가격
with tab_price:
    st.subheader("역산 가격 계산기")
    st.write("현지 소비자가에서 거꾸로 계산해, 우리가 받을 수 있는 FOB 가격을 확인합니다. (마진은 판매가 기준)")

    c1, c2 = st.columns(2)
    with c1:
        retail = st.number_input("현지 소비자가 (세금 제외, USD)", min_value=0.0, value=20.0, step=0.5)
        r_margin = st.slider("리테일러 마진 (%)", 0, 80, 40)
        d_margin = st.slider("총판 마진 (%)", 0, 60, 20)
    with c2:
        duty = st.number_input("수입 관세율 (%)", min_value=0.0, value=12.5, step=0.5)
        other = st.number_input("개당 물류·등록·기타 비용 (USD)", min_value=0.0, value=0.5, step=0.1)
        our_cost = st.number_input("우리 FOB 원가 (제조원가+관리비, USD)", min_value=0.0, value=5.0, step=0.1)

    retailer_buy = retail * (1 - r_margin / 100)
    dist_buy = retailer_buy * (1 - d_margin / 100)
    fob_max = max((dist_buy - other) / (1 + duty / 100), 0.0)
    margin = (fob_max - our_cost) / fob_max * 100 if fob_max > 0 else 0.0

    m1, m2, m3 = st.columns(3)
    m1.metric("리테일러 매입가", f"${retailer_buy:,.2f}")
    m2.metric("총판 매입가", f"${dist_buy:,.2f}")
    m3.metric("수출 가능 FOB 상한", f"${fob_max:,.2f}")
    st.metric("이 가격으로 팔 때 우리 마진", f"{margin:,.1f}%")
    if fob_max > 0 and margin < 0:
        st.error("원가가 FOB 상한보다 높습니다. 소비자가 인상, 용량·구성 변경, 비용 조정이 필요합니다.")
    st.caption("관세율은 FOB에 비례한다고 가정한 단순 계산입니다. 실제 관세와 비용은 관세사와 확인하세요.")

# ---------------------------------------------------------------- 도착 원가
with tab_landed:
    st.subheader("도착 원가 시뮬레이터")
    st.write("바이어 입장에서 제품이 도착했을 때 개당 원가를 계산해, 견적의 경쟁력을 점검합니다.")

    c1, c2 = st.columns(2)
    with c1:
        fob = st.number_input("FOB 단가 (USD)", min_value=0.0, value=8.0, step=0.1)
        qty = st.number_input("수량 (개)", min_value=1, value=5000, step=100)
        freight = st.number_input("국제 운임 총액 (USD)", min_value=0.0, value=1500.0, step=100.0)
        insurance = st.number_input("보험료 총액 (USD)", min_value=0.0, value=100.0, step=10.0)
    with c2:
        basis = st.radio("과세가격 기준", ["FOB 기준 (미국 등)", "CIF 기준 (EU·일본 등)"],
                         help="국가별로 다릅니다. 반드시 [확인]하세요.")
        duty2 = st.number_input("적용 관세율 (%)", min_value=0.0, value=12.5, step=0.5, key="duty2")
        local = st.number_input("현지 통관·내륙 운송·창고 총액 (USD)", min_value=0.0, value=800.0, step=50.0)

    goods = fob * qty
    cif = goods + freight + insurance
    base = goods if basis.startswith("FOB") else cif
    duty_amt = base * duty2 / 100
    total = cif + duty_amt + local

    m1, m2, m3 = st.columns(3)
    m1.metric("CIF 총액", f"${cif:,.0f}")
    m2.metric("관세", f"${duty_amt:,.0f}")
    m3.metric("도착 총원가", f"${total:,.0f}")
    st.metric("개당 도착 원가", f"${total / qty:,.2f}")
    st.caption("미국 관세 구조는 2026년에 여러 번 바뀌었습니다(한국 총 12.5% 구조, 추가 조사 진행 중). 견적 전 최신 내용을 확인하세요.")
