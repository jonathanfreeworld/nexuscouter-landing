import streamlit as st
import math
from chapters import CATEGORIES, CHAPTERS, DEADLINES

st.set_page_config(page_title="K-뷰티·K-푸드 수출 가이드", page_icon="📦", layout="wide")

# ---------------------------------------------------------------- 상단 눈에 띄는 헤더 디자인
st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a, #2563eb); padding: 1.8rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <h1 style="margin: 0; font-size: 1.9rem; font-weight: 700;">📦 K-뷰티·K-푸드 해외영업·수출마케팅 가이드 & 시뮬레이터</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
            일본 · 미국 · 동남아 · 유럽 | 기준일: 2026.10.29 | 규제와 관세는 수시로 변경되니 거래 전 반드시 최신 내용을 확인하세요.
        </p>
    </div>
""", unsafe_allow_html=True)

tab_guide, tab_price, tab_landed = st.tabs(["📖 가이드", "💰 정밀 역산 가격 계산기", "🚢 정밀 도착 원가 시뮬레이터"])

# ---------------------------------------------------------------- 가이드 탭
with tab_guide:
    st.warning("⚠️ **지금 확인해야 할 주요 시한**\n\n" + "\n".join(f"- {d}" for d in DEADLINES))

    st.markdown("#### 🗂️ 카테고리 분류 선택")
    all_cats = ["전체"] + list(CATEGORIES.values())
    cat = st.radio("분류 선택", all_cats, horizontal=True, label_visibility="collapsed")
    
    st.markdown("---")
    q = st.text_input("🔍 검색", placeholder="예: 할랄, MoCRA, FOB, 통관 등 키워드를 입력하세요.")

    # 1. 필터링된 챕터 추출
    filtered_chapters = []
    for ch in CHAPTERS:
        if cat != "전체" and CATEGORIES[ch["cat"]] != cat:
            continue
        text = ch["title"] + ch["summary"] + " ".join(ch["points"])
        if q and q.lower() not in text.lower():
            continue
        filtered_chapters.append(ch)

    # 2. 행열은 유지하되 순서가 위에서 아래로(열 기준) 흐르도록 재배열 (Transpose)
    def transpose_for_columns(item_list, num_cols=3):
        n = len(item_list)
        if n == 0:
            return []
        rows = math.ceil(n / num_cols)
        transposed = []
        for r in range(rows):
            for c in range(num_cols):
                idx = c * rows + r
                if idx < n:
                    transposed.append(item_list[idx])
        return transposed

    display_chapters = transpose_for_columns(filtered_chapters, num_cols=3)

    # 3. 3열(Columns) 그리드 구조로 챕터 배치 및 제목 뒤 (a) 제거 적용
    cols = st.columns(3)
    for idx, ch in enumerate(display_chapters):
        with cols[idx % 3]:
            clean_title = ch['title'].replace(" (a)", "").replace("(a)", "").strip()
            with st.expander(f"제 {ch['no']}장. {clean_title}"):
                st.write(ch["summary"])
                for p in ch["points"]:
                    st.markdown(f"- {p}")
                st.caption("💡 표, 템플릿 및 상세 문서는 버전을 참고하세요.")

# ---------------------------------------------------------------- 역산 가격 계산기 탭 (정밀 버전)
with tab_price:
    st.subheader("💰 정밀 역산 가격 (Reverse Pricing) 계산기")
    st.write("현지 소비자가(Retail Price)에서 출발해 유통 마진, 물류비, 관세 및 수입상 마진을 역으로 차감하여 우리가 확보해야 할 목표 FOB 단가를 정밀 산출합니다.")

    exchange_rate = st.number_input("적용 환율 (KRW / 1 USD)", min_value=100.0, value=1350.0, step=10.0, key="rev_ex")

    st.markdown("---")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("#### 🏷️ 1. 현지 유통 및 소비자가")
        retail_price_usd = st.number_input("현지 소비자가 (세금 제외, USD/Unit)", min_value=0.0, value=25.0, step=0.5)
        retailer_margin_pct = st.slider("리테일러 마진 (%)", 0.0, 80.0, 40.0, step=1.0)
        importer_margin_pct = st.slider("현지 수입상/총판 마진 (%)", 0.0, 60.0, 25.0, step=1.0)

    with c2:
        st.markdown("#### 🚢 2. 물류 및 통관 부대비용")
        est_freight_usd = st.number_input("Unit당 배부 국제운임 (USD/Unit)", min_value=0.0, value=0.4, step=0.05)
        est_insurance_usd = st.number_input("Unit당 배부 해상보험료 (USD/Unit)", min_value=0.0, value=0.05, step=0.01)
        duty_pct = st.number_input("통관 관세율 (%)", min_value=0.0, value=12.5, step=0.5, key="rev_duty")
        est_local_logistics_usd = st.number_input("Unit당 현지 물류/하역/창고비 (USD/Unit)", min_value=0.0, value=0.6, step=0.05)

    with c3:
        st.markdown("#### 🏭 3. 제조 및 마진 검증")
        our_target_cost_krw = st.number_input("우리 제조/출고 원가 (KRW/Unit)", min_value=0.0, value=3500.0, step=100.0)
        target_hq_margin_pct = st.slider("우리(본사) 목표 마진율 (%)", 0.0, 50.0, 15.0, step=1.0)

    retailer_buy_usd = retail_price_usd * (1 - retailer_margin_pct / 100.0)
    importer_buy_usd = retailer_buy_usd * (1 - importer_margin_pct / 100.0)
    cif_target_usd = max((importer_buy_usd - est_local_logistics_usd) / (1 + duty_pct / 100.0), 0.0)
    fob_target_usd = max(cif_target_usd - est_freight_usd - est_insurance_usd, 0.0)
    fob_target_krw = fob_target_usd * exchange_rate

    our_target_cost_usd = our_target_cost_krw / exchange_rate
    achieved_margin_pct = ((fob_target_usd - our_target_cost_usd) / fob_target_usd * 100.0) if fob_target_usd > 0 else 0.0

    st.markdown("---")
    st.markdown("### 📊 역산 가격 시뮬레이션 결과")

    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("리테일러 매입가", f"${retailer_buy_usd:,.2f}")
        st.metric("수입상 매입가 (Landed)", f"${importer_buy_usd:,.2f}")
    with r2:
        st.metric("목표 CIF 단가", f"${cif_target_usd:,.2f}")
        st.metric("목표 수출 FOB 단가", f"₩{fob_target_krw:,.0f} / ${fob_target_usd:,.2f}")
    with r3:
        st.metric("우리 원가 대비 마진율", f"{achieved_margin_pct:,.1f}%")
        st.metric("본사 목표 마진 반영 단가", f"${our_target_cost_usd * (1 + target_hq_margin_pct / 100.0):,.2f}")

    if fob_target_usd > 0 and achieved_margin_pct < target_hq_margin_pct:
        st.error("🚨 역산된 FOB 단가로 산출된 마진이 목표 본사 마진율보다 낮습니다. 현지 소비자가 인상, 유통 마진 조정 또는 원가 절감이 필요합니다.")
    else:
        st.success("✨ 유통 마진과 물류·관세를 감안했을 때 충분한 수익성이 확보되는 구조입니다.")

    st.caption("※ 본 역산 계산기는 현지 유통 구조의 마진과 예상 물류·통관 비용을 일괄 차감하여 산출한 참고용 시뮬레이션입니다.")

# ---------------------------------------------------------------- 도착 원가 시뮬레이터 탭 (정밀 버전)
with tab_landed:
    st.subheader("🚢 정밀 도착 원가 (Landed Cost) 시뮬레이터")
    st.write("제품 규격, 포장 단위, 국내 제조/부대비용부터 해상운송, 관세, 미국 내륙 운송 및 본사/수입상 마진까지 정밀 시뮬레이션합니다.")

    exchange_rate_l = st.number_input("적용 환율 (KRW / 1 USD)", min_value=100.0, value=1350.0, step=10.0, key="land_ex")

    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📦 1. 제품 및 포장 규격")
        weight_g = st.number_input("단위 중량 (g)", min_value=0.0, value=250.0, step=10.0)
        unit_per_case = st.number_input("Unit / Case (개/박스)", min_value=1, value=24, step=1)
        l_mm = st.number_input("박스 가로 (mm)", min_value=1.0, value=400.0, step=10.0)
        w_mm = st.number_input("박스 세로 (mm)", min_value=1.0, value=300.0, step=10.0)
        h_mm = st.number_input("박스 높이 (mm)", min_value=1.0, value=250.0, step=10.0)
        total_cases = st.number_input("총 생산/발주 수량 (Case)", min_value=1, value=500, step=10)
        
        box_cbm = (l_mm * w_mm * h_mm) / 1_000_000_000
        total_cbm = box_cbm * total_cases
        total_units = total_cases * unit_per_case
        st.info(f"📌 박스당 CBM: **{box_cbm:,.4f} m³** | 총 CBM: **{total_cbm:,.2f} m³** | 총 수량: **{total_units:,} Unit**")

    with col2:
        st.markdown("#### 🏭 2. 국내 원가 및 출고 비용")
        product_cost_krw = st.number_input("상품 원가 (KRW/Unit)", min_value=0.0, value=3500.0, step=100.0)
        packing_cost_plt = st.number_input("출고자재비 (KRW/PLT)", min_value=0.0, value=15000.0, step=1000.0)
        loading_cntr = st.number_input("컨테이너 로딩비 (KRW/CNTR)", min_value=0.0, value=250000.0, step=10000.0)
        out_cost_plt = st.number_input("출고비용 (KRW/PLT)", min_value=0.0, value=20000.0, step=1000.0)
        inland_krw = st.number_input("국내 내륙 운송료 (KRW/CNTR)", min_value=0.0, value=350000.0, step=10000.0)

    with col3:
        st.markdown("#### 🚢 3. 해상 및 현지 부대비용")
        export_exp_krw = st.number_input("수출 부대비용 (KRW/CNTR)", min_value=0.0, value=200000.0, step=10000.0)
        port_fee_krw = st.number_input("부두 이용료 (KRW/CNTR)", min_value=0.0, value=150000.0, step=10000.0)
        insurance_usd = st.number_input("해상보험료 (USD/CNTR)", min_value=0.0, value=120.0, step=10.0)
        freight_usd = st.number_input("해상운송료 (USD/CNTR)", min_value=0.0, value=2500.0, step=100.0)
        duty_pct_l = st.number_input("통관 관세율 (%)", min_value=0.0, value=12.5, step=0.5, key="land_duty")

    st.markdown("---")
    col4, col5 = st.columns(2)
    with col4:
        st.markdown("#### 🇺🇸 4. 미국/현지 물류 및 보관 비용")
        us_inland_usd = st.number_input("미국 내륙 운송료 (USD/CNTR)", min_value=0.0, value=1200.0, step=50.0)
        unloading_usd = st.number_input("컨테이너 입고/하역 (USD/CNTR)", min_value=0.0, value=400.0, step=50.0)
        storage_usd_plt_m = st.number_input("창고 보관료 (USD/PLT*M)", min_value=0.0, value=35.0, step=5.0)
    with col5:
        st.markdown("#### 📈 5. 마진 설정")
        hq_margin_pct = st.slider("본사 마진율 (%)", 0.0, 50.0, 15.0, step=1.0, key="land_hq")
        importer_margin_pct = st.slider("수입상 마진율 (%)", 0.0, 50.0, 25.0, step=1.0, key="land_imp")

    total_product_krw = product_cost_krw * total_units
    total_domestic_krw = (packing_cost_plt + out_cost_plt) + loading_cntr + inland_krw + export_exp_krw + port_fee_krw
    
    fob_total_krw = total_product_krw + total_domestic_krw
    fob_unit_krw = fob_total_krw / total_units
    fob_unit_usd = fob_unit_krw / exchange_rate_l
    fob_case_krw = fob_unit_krw * unit_per_case
    fob_case_usd = fob_unit_usd * unit_per_case

    insurance_krw = insurance_usd * exchange_rate_l
    freight_krw = freight_usd * exchange_rate_l
    cif_total_krw = fob_total_krw + insurance_krw + freight_krw
    cif_unit_krw = cif_total_krw / total_units
    cif_unit_usd = cif_unit_krw / exchange_rate_l
    cif_case_krw = cif_unit_krw * unit_per_case
    cif_case_usd = cif_unit_usd * unit_per_case

    duty_krw = cif_total_krw * (duty_pct_l / 100.0)

    local_logistics_usd = us_inland_usd + unloading_usd + (storage_usd_plt_m * (total_cases / 40))
    local_logistics_krw = local_logistics_usd * exchange_rate_l

    landed_total_krw = cif_total_krw + duty_krw + local_logistics_krw
    landed_unit_krw = landed_total_krw / total_units
    landed_unit_usd = landed_unit_krw / exchange_rate_l
    landed_case_krw = landed_unit_krw * unit_per_case
    landed_case_usd = landed_unit_usd * unit_per_case

    hq_margin_unit_usd = fob_unit_usd * (1 + hq_margin_pct / 100.0)
    hq_margin_case_usd = hq_margin_unit_usd * unit_per_case

    importer_margin_unit_usd = landed_unit_usd * (1 + importer_margin_pct / 100.0)
    importer_margin_case_usd = importer_margin_unit_usd * unit_per_case

    st.markdown("---")
    st.markdown("### 📊 시뮬레이터 최종 결과 요약")

    res1, res2, res3 = st.columns(3)
    with res1:
        st.metric("FOB (Unit)", f"₩{fob_unit_krw:,.0f} / ${fob_unit_usd:,.2f}")
        st.metric("FOB (Case)", f"₩{fob_case_krw:,.0f} / ${fob_case_usd:,.2f}")
    with res2:
        st.metric("CIF (Unit)", f"₩{cif_unit_krw:,.0f} / ${cif_unit_usd:,.2f}")
        st.metric("CIF (Case)", f"₩{cif_case_krw:,.0f} / ${cif_case_usd:,.2f}")
    with res3:
        st.metric("Landed Cost (Unit)", f"₩{landed_unit_krw:,.0f} / ${landed_unit_usd:,.2f}")
        st.metric("Landed Cost (Case)", f"₩{landed_case_krw:,.0f} / ${landed_case_usd:,.2f}")

    st.markdown("---")
    st.markdown("#### 💡 마진 반영 단가 분석")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.success(f"**본사 마진 반영가 ({hq_margin_pct}%)**\n- Unit: **${hq_margin_unit_usd:,.2f}**\n- Case: **${hq_margin_case_usd:,.2f}**")
    with m_col2:
        st.warning(f"**수입상 마진 반영가 ({importer_margin_pct}%)**\n- Unit: **${importer_margin_unit_usd:,.2f}**\n- Case: **${importer_margin_case_usd:,.2f}**")
    
    st.caption("※ 본 시뮬레이터는 입력된 규격, 물류비, 관세 및 마진율을 토대로 산출된 참고용 데이터입니다. 실제 계약 및 견적 시 포워더 및 관세사를 통해 최종 비용을 검증하세요.")
