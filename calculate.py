import math
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

# chapters.py에서 가이드 데이터 불러오기
from chapters import CATEGORIES, CHAPTERS, DEADLINES

st.set_page_config(
    page_title="해외 수출 컨테이너 혼재 적재 및 원가 시뮬레이터",
    layout="wide",
)

# ---------------------------------------------------------------- 상단 눈에 띄는 헤더 및 공통 환율 설정
st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a, #2563eb); padding: 1.8rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <h1 style="margin: 0; font-size: 1.9rem; font-weight: 700;">📦 해외 수출 컨테이너 혼재 적재 및 원가 통합 시뮬레이터</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
            수출마케팅 가이드부터 컨테이너 적재 입수량 산출, 역산 가격, 정밀 도착 원가(Landed Cost)까지 하나의 플랫폼에서 연동하세요.
        </p>
    </div>
""", unsafe_allow_html=True)

# 공통 환율 입력 바 (모든 탭에서 공유)
col_ex1, col_ex2, col_ex3 = st.columns([1, 2, 2])
with col_ex1:
    GLOBAL_EXCHANGE_RATE = st.number_input(
        "💱 적용 환율 (KRW / 1 USD)",
        min_value=100.0,
        value=1350.0,
        step=10.0,
        help="모든 시뮬레이터와 가격 계산에 공통으로 반영되는 기준 환율입니다."
    )

st.markdown("---")

# 탭 구성
tab_guide, tab_load, tab_price, tab_landed = st.tabs([
    "📖 수출마케팅 가이드", 
    "📦 컨테이너 혼재 적재 시뮬레이터", 
    "💰 정밀 역산 가격 계산기", 
    "🚢 정밀 도착 원가 (Landed Cost)"
])


# ================================================================ 1. 수출마케팅 가이드 탭
with tab_guide:
    st.warning("⚠️ **지금 확인해야 할 주요 시한**\n\n" + "\n".join(f"- {d}" for d in DEADLINES))

    st.markdown("#### 🗂️ 카테고리 분류 선택")
    all_cats = ["전체"] + list(CATEGORIES.values())
    cat = st.radio("분류 선택", all_cats, horizontal=True, label_visibility="collapsed")
    
    st.markdown("---")
    q = st.text_input("🔍 검색", placeholder="예: 할랄, MoCRA, FOB, 통관 등 키워드를 입력하세요.")

    filtered_chapters = []
    for ch in CHAPTERS:
        if cat != "전체" and CATEGORIES[ch["cat"]] != cat:
            continue
        text = ch["title"] + ch["summary"] + " ".join(ch["points"])
        if q and q.lower() not in text.lower():
            continue
        filtered_chapters.append(ch)

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

    cols = st.columns(3)
    for idx, ch in enumerate(display_chapters):
        with cols[idx % 3]:
            clean_title = ch['title'].replace(" (a)", "").replace("(a)", "").strip()
            with st.expander(f"제 {ch['no']}장. {clean_title}"):
                st.write(ch["summary"])
                for p in ch["points"]:
                    st.markdown(f"- {p}")
                st.caption("💡 표, 템플릿 및 상세 문서는 버전을 참고하세요.")


# ================================================================ 2. 컨테이너 혼재 적재 시뮬레이터 탭
CONTAINER_SPECS = {
    "20ft Standard": {"length": 5898, "width": 2352, "height": 2393, "max_payload": 28000, "cbm": 33.2},
    "40ft Standard": {"length": 12032, "width": 2352, "height": 2393, "max_payload": 28800, "cbm": 67.7},
    "40ft High Cube (HQ)": {"length": 12032, "width": 2352, "height": 2698, "max_payload": 28600, "cbm": 76.3},
}

def get_layer_capacity(pallet_l, pallet_w, box_l, box_w):
    if box_l <= 0 or box_w <= 0:
        return 0, "해당 없음"
    layout_1 = (pallet_l // box_l) * (pallet_w // box_w)
    layout_2 = (pallet_l // box_w) * (pallet_w // box_l)
    return (layout_1, "기본 방향") if layout_1 >= layout_2 else (layout_2, "90도 회전")

def get_floor_pallet_capacity(container_length, container_width, pallet_l, pallet_w):
    layout_1 = (container_length // pallet_l) * (container_width // pallet_w)
    layout_2 = (container_length // pallet_w) * (container_width // pallet_l)
    return (layout_1, "기본 방향") if layout_1 >= layout_2 else (layout_2, "파레트 90도 회전")

def calculate_mixed_pallet_plan(sku_inputs, pallet_l, pallet_w, pallet_height, pallet_weight, max_stack_height, pallet_max_load):
    if max_stack_height <= pallet_height:
        raise ValueError("파레트 총 적재 제한 높이는 빈 파레트 높이보다 커야 합니다.")
    available_height = max_stack_height - pallet_height
    max_cargo_weight = pallet_max_load - pallet_weight
    if max_cargo_weight <= 0:
        raise ValueError("파레트 자체 중량이 파레트 최대 총중량 이상입니다.")

    sku_meta = []
    layer_units = []
    for sku_index, (name, box_l, box_w, box_h, box_weight, qty) in enumerate(sku_inputs):
        if qty == 0 or box_l == 0 or box_w == 0 or box_h == 0:
            sku_meta.append({"name": name or f"SKU {sku_index + 1}", "box_l": box_l, "box_w": box_w, "box_h": box_h, "box_weight": box_weight, "qty": 0, "cbm": 0.0, "cargo_weight": 0.0, "layer_capacity": 0, "layers": 0, "pallet_layout": "해당 없음", "boxes_per_pallet_geometry": 0, "effective_layer_capacity": 0})
            continue

        layer_capacity, pallet_layout = get_layer_capacity(pallet_l, pallet_w, box_l, box_w)
        layers_by_height = available_height // box_h
        max_boxes_by_weight = math.floor(max_cargo_weight / box_weight)
        effective_layer_capacity = min(layer_capacity, max_boxes_by_weight)
        
        remaining = int(qty)
        sku_layer_count = 0
        while remaining > 0:
            boxes_in_layer = min(remaining, effective_layer_capacity)
            layer_units.append({"sku_index": sku_index, "sku_name": name or f"SKU {sku_index + 1}", "boxes": boxes_in_layer, "height": box_h, "cargo_weight": boxes_in_layer * box_weight})
            remaining -= boxes_in_layer
            sku_layer_count += 1

        sku_meta.append({
            "name": name or f"SKU {sku_index + 1}", "box_l": box_l, "box_w": box_w, "box_h": box_h, "box_weight": box_weight, "qty": int(qty),
            "cbm": qty * box_l * box_w * box_h / 1_000_000_000, "cargo_weight": qty * box_weight, "layer_capacity": layer_capacity,
            "layers": sku_layer_count, "pallet_layout": pallet_layout, "boxes_per_pallet_geometry": layer_capacity * layers_by_height,
            "effective_layer_capacity": effective_layer_capacity
        })

    layer_units.sort(key=lambda unit: (unit["height"], unit["cargo_weight"]), reverse=True)
    mixed_pallets = []
    for unit in layer_units:
        candidates = []
        for pallet_index, pallet in enumerate(mixed_pallets):
            rem_h = available_height - pallet["height"]
            rem_w = max_cargo_weight - pallet["cargo_weight"]
            if unit["height"] <= rem_h and unit["cargo_weight"] <= rem_w:
                candidates.append((rem_h - unit["height"], rem_w - unit["cargo_weight"], pallet_index))
        if candidates:
            _, _, p_idx = min(candidates)
            target = mixed_pallets[p_idx]
        else:
            target = {"height": 0, "cargo_weight": 0.0, "layers": []}
            mixed_pallets.append(target)
        target["height"] += unit["height"]
        target["cargo_weight"] += unit["cargo_weight"]
        target["layers"].append(unit)

    results = []
    for sku_index, meta in enumerate(sku_meta):
        pallets_with_sku = sum(any(layer["sku_index"] == sku_index for layer in p["layers"]) for p in mixed_pallets)
        results.append({
            "name": meta["name"], "boxes": meta["qty"], "cbm": meta["cbm"], "cargo_weight": meta["cargo_weight"],
            "pallets": pallets_with_sku, "pallet_weight": pallets_with_sku * pallet_weight, "layer_capacity": meta["layer_capacity"],
            "layers": meta["layers"], "boxes_per_pallet_geometry": meta["boxes_per_pallet_geometry"],
            "boxes_per_pallet": (meta["qty"] / pallets_with_sku if pallets_with_sku else 0),
            "pallet_layout": meta["pallet_layout"], "max_cargo_weight_per_pallet": max_cargo_weight,
            "mixed_pallets": pallets_with_sku, "effective_layer_capacity": meta["effective_layer_capacity"]
        })
    return results, mixed_pallets

def create_excel_report(selected_container, container, results, mixed_pallets, total_boxes, total_cbm, total_cargo_weight, total_pallets, total_pallet_weight, total_weight, base_pallet_capacity, effective_pallet_capacity, pallet_layout, cbm_rate, is_cbm_ok, is_weight_ok, is_pallet_ok, is_double_stack, safety_margin, pallet_l, pallet_w, pallet_height, pallet_weight, max_stack_height, pallet_max_load):
    output = BytesIO()
    overall_ok = is_cbm_ok and is_weight_ok and is_pallet_ok and total_boxes > 0
    summary_df = pd.DataFrame([
        ["시뮬레이션 일시", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["컨테이너", selected_container],
        ["최종 판정", "적합" if overall_ok else "검토 필요"],
        ["총 박스 수", total_boxes],
        ["총 필요 파레트 수", total_pallets],
        ["안전 마진 반영 파레트 한도", effective_pallet_capacity],
        ["이론 화물 CBM", round(total_cbm, 3)],
        ["컨테이너 명목 CBM", container["cbm"]],
        ["이론 CBM 비율(%)", round(cbm_rate, 1)],
        ["화물 순중량(kg)", round(total_cargo_weight, 2)],
        ["파레트 총중량(kg)", round(total_pallet_weight, 2)],
        ["총 선적중량(kg)", round(total_weight, 2)],
        ["허용 화물중량(kg)", container["max_payload"]],
    ], columns=["항목", "값"])

    sku_rows = []
    for item in results:
        if item["boxes"] > 0:
            sku_rows.append({
                "SKU/품목명": item["name"], "박스 수량": int(item["boxes"]), "필요 파레트 수": int(item["pallets"]),
                "박스 CBM": round(item["cbm"], 3), "화물중량(kg)": round(item["cargo_weight"], 2),
                "파레트당 1층 수량": int(item["layer_capacity"]), "적재 층수": int(item["layers"]),
                "기하학적 파레트당 최대 수량": int(item["boxes_per_pallet_geometry"]), "최종 파레트당 적용 수량": int(item["boxes_per_pallet"]),
                "파레트 배치 방향": item["pallet_layout"], "파레트당 허용 화물중량(kg)": round(item["max_cargo_weight_per_pallet"], 2)
            })
    sku_df = pd.DataFrame(sku_rows)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="종합 결과", index=False)
        sku_df.to_excel(writer, sheet_name="SKU별 상세", index=False)
    return output.getvalue()

with tab_load:
    st.subheader("📦 컨테이너 혼재 적재 시뮬레이터")
    with st.form("mixed_simulation_form"):
        st.markdown("#### 1. 3개 품목(SKU) 규격 및 선적 목표 수량")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown("**품목 1**")
            name_1 = st.text_input("품목 1 이름", value="프리미엄 크림", key="n1")
            l1 = st.number_input("박스 길이 (mm)", min_value=0, value=400, key="l1")
            w1 = st.number_input("박스 너비 (mm)", min_value=0, value=300, key="w1")
            h1 = st.number_input("박스 높이 (mm)", min_value=0, value=250, key="h1")
            wt1 = st.number_input("박스 1개 무게 (kg)", min_value=0.0, value=15.0, key="wt1")
            qty_1 = st.number_input("선적 목표 박스 수량", min_value=0, value=300, key="qty1")
        with sc2:
            st.markdown("**품목 2**")
            name_2 = st.text_input("품목 2 이름", value="기능성 앰플", key="n2")
            l2 = st.number_input("박스 길이 (mm)", min_value=0, value=0, key="l2")
            w2 = st.number_input("박스 너비 (mm)", min_value=0, value=0, key="w2")
            h2 = st.number_input("박스 높이 (mm)", min_value=0, value=0, key="h2")
            wt2 = st.number_input("박스 1개 무게 (kg)", min_value=0.0, value=0.0, key="wt2")
            qty_2 = st.number_input("선적 목표 박스 수량", min_value=0, value=0, key="qty2")
        with sc3:
            st.markdown("**품목 3**")
            name_3 = st.text_input("품목 3 이름", value="마스크팩 세트", key="n3")
            l3 = st.number_input("박스 길이 (mm)", min_value=0, value=0, key="l3")
            w3 = st.number_input("박스 너비 (mm)", min_value=0, value=0, key="w3")
            h3 = st.number_input("박스 높이 (mm)", min_value=0, value=0, key="h3")
            wt3 = st.number_input("박스 1개 무게 (kg)", min_value=0.0, value=0.0, key="wt3")
            qty_3 = st.number_input("선적 목표 박스 수량", min_value=0, value=0, key="qty3")

        st.divider()
        pc1, pc2 = st.columns(2)
        with pc1:
            st.subheader("2. 파레트 옵션")
            pallet_l = st.number_input("파레트 길이 (mm)", min_value=1, value=1100)
            pallet_w = st.number_input("파레트 너비 (mm)", min_value=1, value=1100)
            pallet_height = st.number_input("빈 파레트 높이 (mm)", min_value=1, value=150)
            pallet_weight = st.number_input("빈 파레트 무게 (kg)", min_value=0.1, value=20.0)
            max_stack_height = st.number_input("파레트 총 적재 제한 높이 (mm)", min_value=1, value=1600)
            pallet_max_load = st.number_input("파레트 최대 총중량 (kg)", min_value=1.0, value=1000.0)
        with pc2:
            st.subheader("3. 컨테이너 및 적재 방식")
            selected_container = st.selectbox("타겟 컨테이너 종류", list(CONTAINER_SPECS.keys()))
            is_double_stack = st.checkbox("🔄 파레트 2단 적재 (Double Stacking)", value=False)
            safety_margin = st.slider("파레트 수용량 안전 마진 (%)", 0, 20, 5)

        submitted = st.form_submit_button("🚀 혼재 적재 시뮬레이션 실행")

    if submitted:
        container = CONTAINER_SPECS[selected_container]
        try:
            sku_inputs = [(name_1, l1, w1, h1, wt1, qty_1), (name_2, l2, w2, h2, wt2, qty_2), (name_3, l3, w3, h3, wt3, qty_3)]
            results, mixed_pallets = calculate_mixed_pallet_plan(sku_inputs, pallet_l, pallet_w, pallet_height, pallet_weight, max_stack_height, pallet_max_load)
        except ValueError as exc:
            st.error(f"❌ 입력값 검증 오류: {exc}")
            st.stop()

        total_boxes = sum(item["boxes"] for item in results)
        total_cbm = sum(item["cbm"] for item in results)
        total_cargo_weight = sum(item["cargo_weight"] for item in results)
        total_pallets = len(mixed_pallets)
        total_pallet_weight = total_pallets * pallet_weight
        total_weight = total_cargo_weight + total_pallet_weight

        base_pallet_capacity, pallet_layout = get_floor_pallet_capacity(container["length"], container["width"], pallet_l, pallet_w)
        physical_pallet_capacity = base_pallet_capacity * 2 if is_double_stack else base_pallet_capacity
        effective_pallet_capacity = math.floor(physical_pallet_capacity * (1 - safety_margin / 100))

        st.divider()
        st.subheader(f"📊 [{selected_container}] 시뮬레이션 결과 요약")
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown("#### 📦 품목별 집계")
            for item in results:
                if item["boxes"] > 0:
                    st.write(f"- **{item['name']}**: {int(item['boxes']):,}박스 / {int(item['pallets']):,}파레트")
            st.write(f"- **총 박스 수**: **{total_boxes:,}개**")
        with rc2:
            st.markdown("#### 🚢 공간 및 파레트")
            st.write(f"- 필요 파레트: **{total_pallets:,}개** (한도: {effective_pallet_capacity:,}개)")
            st.write(f"- 이론 화물 CBM: **{total_cbm:.2f} CBM** (컨테이너 명목: {container['cbm']} CBM)")
            cbm_rate = (total_cbm / container["cbm"] * 100) if container["cbm"] else 0
            st.write(f"- CBM 적재율: **{cbm_rate:.1f}%**")
        with rc3:
            st.markdown("#### ⚖️ 중량")
            st.write(f"- 화물 순중량: {total_cargo_weight:,.2f} kg")
            st.write(f"- 총 선적중량(파레트 포함): **{total_weight:,.2f} kg**")
            st.write(f"- 허용 화물중량: {container['max_payload']:,} kg")


# ================================================================ 3. 정밀 역산 가격 계산기 탭
with tab_price:
    st.subheader("💰 정밀 역산 가격 (Reverse Pricing) 계산기")
    st.write("현지 소비자가(Retail Price)에서 출발해 유통 마진, 물류비, 관세 및 수입상 마진을 차감하여 목표 FOB 단가를 산출합니다.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🏷️ 1. 유통 및 소비자가")
        retail_price_usd = st.number_input("현지 소비자가 (세금 제외, USD/Unit)", min_value=0.0, value=25.0, step=0.5)
        retailer_margin_pct = st.slider("리테일러 마진 (%)", 0.0, 80.0, 40.0, step=1.0)
        importer_margin_pct = st.slider("현지 수입상/총판 마진 (%)", 0.0, 60.0, 25.0, step=1.0)
    with c2:
        st.markdown("#### 🚢 2. 물류 및 통관 비용")
        est_freight_usd = st.number_input("Unit당 배부 국제운임 (USD/Unit)", min_value=0.0, value=0.4, step=0.05)
        est_insurance_usd = st.number_input("Unit당 배부 해상보험료 (USD/Unit)", min_value=0.0, value=0.05, step=0.01)
        duty_pct = st.number_input("통관 관세율 (%)", min_value=0.0, value=12.5, step=0.5)
        est_local_logistics_usd = st.number_input("Unit당 현지 물류/하역/창고비 (USD/Unit)", min_value=0.0, value=0.6, step=0.05)
    with c3:
        st.markdown("#### 🏭 3. 제조 원가 및 마진 검증")
        our_target_cost_krw = st.number_input("우리 제조/출고 원가 (KRW/Unit)", min_value=0.0, value=3500.0, step=100.0)
        target_hq_margin_pct = st.slider("우리(본사) 목표 마진율 (%)", 0.0, 50.0, 15.0, step=1.0)

    retailer_buy_usd = retail_price_usd * (1 - retailer_margin_pct / 100.0)
    importer_buy_usd = retailer_buy_usd * (1 - importer_margin_pct / 100.0)
    cif_target_usd = max((importer_buy_usd - est_local_logistics_usd) / (1 + duty_pct / 100.0), 0.0)
    fob_target_usd = max(cif_target_usd - est_freight_usd - est_insurance_usd, 0.0)
    fob_target_krw = fob_target_usd * GLOBAL_EXCHANGE_RATE

    our_target_cost_usd = our_target_cost_krw / GLOBAL_EXCHANGE_RATE
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
        st.error("🚨 역산된 FOB 단가로 산출된 마진이 목표 본사 마진율보다 낮습니다. 소비자가 인상 또는 원가 절감이 필요합니다.")
    else:
        st.success("✨ 유통 마진과 물류·관세를 감안했을 때 충분한 수익성이 확보되는 구조입니다.")


# ================================================================ 4. 정밀 도착 원가 시뮬레이터 탭
with tab_landed:
    st.subheader("🚢 정밀 도착 원가 (Landed Cost) 시뮬레이터")
    st.write("박스 규격 및 컨테이너 입수량을 기준으로 국내 제조비, 해상운송, 관세, 현지 하역 및 마진까지 통합 산출합니다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 📦 1. 제품 및 포장 규격")
        weight_g = st.number_input("단위 중량 (g)", min_value=0.0, value=250.0, step=10.0, key="lw")
        unit_per_case = st.number_input("Unit / Case (개/박스)", min_value=1, value=24, step=1, key="lupc")
        l_mm = st.number_input("박스 가로 (mm)", min_value=1.0, value=400.0, step=10.0, key="ll")
        w_mm = st.number_input("박스 세로 (mm)", min_value=1.0, value=300.0, step=10.0, key="lwid")
        h_mm = st.number_input("박스 높이 (mm)", min_value=1.0, value=250.0, step=10.0, key="lh")
        total_cases = st.number_input("총 생산/발주 수량 (Case)", min_value=1, value=500, step=10, key="ltc")
        
        total_units = total_cases * unit_per_case
        st.info(f"📌 총 입수량: **{total_units:,} Unit** (박스당 {unit_per_case}개)")
    with col2:
        st.markdown("#### 🏭 2. 국내 원가 및 출고 비용")
        product_cost_krw = st.number_input("상품 원가 (KRW/Unit)", min_value=0.0, value=3500.0, step=100.0, key="lpc")
        packing_cost_plt = st.number_input("출고자재비 (KRW/PLT)", min_value=0.0, value=15000.0, step=1000.0, key="lpk")
        loading_cntr = st.number_input("컨테이너 로딩비 (KRW/CNTR)", min_value=0.0, value=250000.0, step=10000.0, key="llc")
        out_cost_plt = st.number_input("출고비용 (KRW/PLT)", min_value=0.0, value=20000.0, step=1000.0, key="loc")
        inland_krw = st.number_input("국내 내륙 운송료 (KRW/CNTR)", min_value=0.0, value=350000.0, step=10000.0, key="lik")
    with col3:
        st.markdown("#### 🚢 3. 해상 및 현지 부대비용")
        export_exp_krw = st.number_input("수출 부대비용 (KRW/CNTR)", min_value=0.0, value=200000.0, step=10000.0, key="lee")
        port_fee_krw = st.number_input("부두 이용료 (KRW/CNTR)", min_value=0.0, value=150000.0, step=10000.0, key="lpf")
        insurance_usd = st.number_input("해상보험료 (USD/CNTR)", min_value=0.0, value=120.0, step=10.0, key="liu")
        freight_usd = st.number_input("해상운송료 (USD/CNTR)", min_value=0.0, value=2500.0, step=100.0, key="lfu")
        duty_pct_l = st.number_input("통관 관세율 (%)", min_value=0.0, value=12.5, step=0.5, key="lduty")

    st.markdown("---")
    col4, col5 = st.columns(2)
    with col4:
        st.markdown("#### 🇺🇸 4. 미국/현지 물류 및 보관 비용")
        us_inland_usd = st.number_input("미국 내륙 운송료 (USD/CNTR)", min_value=0.0, value=1200.0, step=50.0, key="lui")
        unloading_usd = st.number_input("컨테이너 입고/하역 (USD/CNTR)", min_value=0.0, value=400.0, step=50.0, key="luu")
        storage_usd_plt_m = st.number_input("창고 보관료 (USD/PLT*M)", min_value=0.0, value=35.0, step=5.0, key="lsu")
    with col5:
        st.markdown("#### 📈 5. 마진 설정")
        hq_margin_pct = st.slider("본사 마진율 (%)", 0.0, 50.0, 15.0, step=1.0, key="lhq")
        importer_margin_pct = st.slider("수입상 마진율 (%)", 0.0, 50.0, 25.0, step=1.0, key="limp")

    total_product_krw = product_cost_krw * total_units
    total_domestic_krw = packing_cost_plt + out_cost_plt + loading_cntr + inland_krw + export_exp_krw + port_fee_krw
    
    fob_total_krw = total_product_krw + total_domestic_krw
    fob_unit_krw = fob_total_krw / total_units if total_units > 0 else 0
    fob_unit_usd = fob_unit_krw / GLOBAL_EXCHANGE_RATE
    fob_case_krw = fob_unit_krw * unit_per_case
    fob_case_usd = fob_unit_usd * unit_per_case

    insurance_krw = insurance_usd * GLOBAL_EXCHANGE_RATE
    freight_krw = freight_usd * GLOBAL_EXCHANGE_RATE
    cif_total_krw = fob_total_krw + insurance_krw + freight_krw
    cif_unit_krw = cif_total_krw / total_units if total_units > 0 else 0
    cif_unit_usd = cif_unit_krw / GLOBAL_EXCHANGE_RATE
    cif_case_krw = cif_unit_krw * unit_per_case
    cif_case_usd = cif_unit_usd * unit_per_case

    duty_krw = cif_total_krw * (duty_pct_l / 100.0)
    local_logistics_usd = us_inland_usd + unloading_usd + (storage_usd_plt_m * (total_cases / 40))
    local_logistics_krw = local_logistics_usd * GLOBAL_EXCHANGE_RATE

    landed_total_krw = cif_total_krw + duty_krw + local_logistics_krw
    landed_unit_krw = landed_total_krw / total_units if total_units > 0 else 0
    landed_unit_usd = landed_unit_krw / GLOBAL_EXCHANGE_RATE
    landed_case_krw = landed_unit_krw * unit_per_case
    landed_case_usd = landed_unit_usd * unit_per_case

    hq_margin_unit_usd = fob_unit_usd * (1 + hq_margin_pct / 100.0)
    hq_margin_case_usd = hq_margin_unit_usd * unit_per_case
    importer_margin_unit_usd = landed_unit_usd * (1 + importer_margin_pct / 100.0)
    importer_margin_case_usd = importer_margin_unit_usd * unit_per_case

    st.markdown("---")
    st.markdown("### 📊 정밀 도착 원가 최종 결과 요약")
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
    st.markdown("#### 💡 마진 반영 최종 단가 분석")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.success(f"**본사 마진 반영가 ({hq_margin_pct}%)**\n- Unit: **${hq_margin_unit_usd:,.2f}**\n- Case: **${hq_margin_case_usd:,.2f}**")
    with m_col2:
        st.warning(f"**수입상 마진 반영가 ({importer_margin_pct}%)**\n- Unit: **${importer_margin_unit_usd:,.2f}**\n- Case: **${importer_margin_case_usd:,.2f}**")
