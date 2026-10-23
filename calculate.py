import math
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="컨테이너 혼재 적재 시뮬레이터",
    layout="wide",
)

st.title("📦 해외 수출 컨테이너 혼재 적재 시뮬레이터")
st.caption(
    "3개 SKU를 공용 파레트의 서로 다른 층에 혼재 적재한다고 가정하여, "
    "이론 CBM·중량·파레트 수용량·높이 조건을 검토합니다."
)


# 컨테이너 내경 기준(mm), 허용 화물중량(파레트 포함, kg), 명목 CBM
CONTAINER_SPECS = {
    "20ft Standard": {
        "length": 5898,
        "width": 2352,
        "height": 2393,
        "max_payload": 28000,
        "cbm": 33.2,
    },
    "40ft Standard": {
        "length": 12032,
        "width": 2352,
        "height": 2393,
        "max_payload": 28800,
        "cbm": 67.7,
    },
    "40ft High Cube (HQ)": {
        "length": 12032,
        "width": 2352,
        "height": 2698,
        "max_payload": 28600,
        "cbm": 76.3,
    },
}


def get_layer_capacity(
    pallet_l: int,
    pallet_w: int,
    box_l: int,
    box_w: int,
) -> Tuple[int, str]:
    """박스 방향을 90도 회전하는 경우까지 고려한 1층 적재 수량을 반환합니다."""
    if box_l <= 0 or box_w <= 0:
        return 0, "해당 없음"
    layout_1 = (pallet_l // box_l) * (pallet_w // box_w)
    layout_2 = (pallet_l // box_w) * (pallet_w // box_l)

    if layout_1 >= layout_2:
        return layout_1, "기본 방향"
    return layout_2, "90도 회전"


def get_floor_pallet_capacity(
    container_length: int,
    container_width: int,
    pallet_l: int,
    pallet_w: int,
) -> Tuple[int, str]:
    """파레트 방향을 회전하는 경우까지 고려한 컨테이너 바닥 수용량."""
    layout_1 = (container_length // pallet_l) * (container_width // pallet_w)
    layout_2 = (container_length // pallet_w) * (container_width // pallet_l)

    if layout_1 >= layout_2:
        return layout_1, "기본 방향"
    return layout_2, "파레트 90도 회전"


def calculate_mixed_pallet_plan(
    sku_inputs: List[Tuple[str, int, int, int, float, int]],
    pallet_l: int,
    pallet_w: int,
    pallet_height: int,
    pallet_weight: float,
    max_stack_height: int,
    pallet_max_load: float,
) -> Tuple[List[Dict[str, float]], List[Dict[str, object]]]:
    """여러 SKU의 적재 층을 공용 파렛트에 배치하는 혼재 파렛트 계산입니다."""
    if max_stack_height <= pallet_height:
        raise ValueError("파레트 총 적재 제한 높이는 빈 파레트 높이보다 커야 합니다.")

    available_height = max_stack_height - pallet_height
    max_cargo_weight = pallet_max_load - pallet_weight
    if max_cargo_weight <= 0:
        raise ValueError("파레트 자체 중량이 파레트 최대 총중량 이상입니다.")

    sku_meta = []
    layer_units = []

    for sku_index, (name, box_l, box_w, box_h, box_weight, qty) in enumerate(
        sku_inputs
    ):
        if qty == 0 or box_l == 0 or box_w == 0 or box_h == 0:
            sku_meta.append(
                {
                    "name": name or f"SKU {sku_index + 1}",
                    "box_l": box_l,
                    "box_w": box_w,
                    "box_h": box_h,
                    "box_weight": box_weight,
                    "qty": 0,
                    "cbm": 0.0,
                    "cargo_weight": 0.0,
                    "layer_capacity": 0,
                    "layers": 0,
                    "pallet_layout": "해당 없음",
                    "boxes_per_pallet_geometry": 0,
                    "effective_layer_capacity": 0,
                }
            )
            continue

        if qty < 0:
            raise ValueError(f"{name or 'SKU'}의 수량은 0 이상이어야 합니다.")
        if box_weight <= 0:
            raise ValueError(f"{name or 'SKU'}의 박스 중량은 0보다 커야 합니다.")

        layer_capacity, pallet_layout = get_layer_capacity(
            pallet_l, pallet_w, box_l, box_w
        )
        if layer_capacity <= 0:
            raise ValueError(
                f"{name or 'SKU'} 박스({box_l}×{box_w}mm)가 "
                f"파레트({pallet_l}×{pallet_w}mm)에 들어가지 않습니다."
            )

        layers_by_height = available_height // box_h
        if layers_by_height <= 0:
            raise ValueError(
                f"{name or 'SKU'} 박스 높이({box_h:,}mm)가 "
                f"파레트 적재 가능 높이({available_height:,}mm)를 초과합니다."
            )

        max_boxes_by_weight = math.floor(max_cargo_weight / box_weight)
        if max_boxes_by_weight <= 0:
            raise ValueError(
                f"{name or 'SKU'} 박스 1개 중량이 파레트 허용 화물중량을 초과합니다."
            )

        effective_layer_capacity = min(layer_capacity, max_boxes_by_weight)
        remaining = int(qty)
        sku_layer_count = 0
        while remaining > 0:
            boxes_in_layer = min(remaining, effective_layer_capacity)
            layer_units.append(
                {
                    "sku_index": sku_index,
                    "sku_name": name or f"SKU {sku_index + 1}",
                    "boxes": boxes_in_layer,
                    "height": box_h,
                    "cargo_weight": boxes_in_layer * box_weight,
                }
            )
            remaining -= boxes_in_layer
            sku_layer_count += 1

        sku_meta.append(
            {
                "name": name or f"SKU {sku_index + 1}",
                "box_l": box_l,
                "box_w": box_w,
                "box_h": box_h,
                "box_weight": box_weight,
                "qty": int(qty),
                "cbm": qty * box_l * box_w * box_h / 1_000_000_000,
                "cargo_weight": qty * box_weight,
                "layer_capacity": layer_capacity,
                "layers": sku_layer_count,
                "pallet_layout": pallet_layout,
                "boxes_per_pallet_geometry": layer_capacity * layers_by_height,
                "effective_layer_capacity": effective_layer_capacity,
            }
        )

    layer_units.sort(
        key=lambda unit: (unit["height"], unit["cargo_weight"]),
        reverse=True,
    )

    mixed_pallets: List[Dict[str, object]] = []
    for unit in layer_units:
        candidates = []
        for pallet_index, pallet in enumerate(mixed_pallets):
            remaining_height = available_height - pallet["height"]
            remaining_weight = max_cargo_weight - pallet["cargo_weight"]
            if (
                unit["height"] <= remaining_height
                and unit["cargo_weight"] <= remaining_weight
            ):
                candidates.append(
                    (
                        remaining_height - unit["height"],
                        remaining_weight - unit["cargo_weight"],
                        pallet_index,
                    )
                )

        if candidates:
            _, _, pallet_index = min(candidates)
            target = mixed_pallets[pallet_index]
        else:
            target = {
                "height": 0,
                "cargo_weight": 0.0,
                "layers": [],
            }
            mixed_pallets.append(target)

        target["height"] += unit["height"]
        target["cargo_weight"] += unit["cargo_weight"]
        target["layers"].append(unit)

    results = []
    for sku_index, meta in enumerate(sku_meta):
        pallets_with_sku = sum(
            any(layer["sku_index"] == sku_index for layer in pallet["layers"])
            for pallet in mixed_pallets
        )
        results.append(
            {
                "name": meta["name"],
                "boxes": meta["qty"],
                "cbm": meta["cbm"],
                "cargo_weight": meta["cargo_weight"],
                "pallets": pallets_with_sku,
                "pallet_weight": pallets_with_sku * pallet_weight,
                "layer_capacity": meta["layer_capacity"],
                "layers": meta["layers"],
                "boxes_per_pallet_geometry": meta["boxes_per_pallet_geometry"],
                "boxes_per_pallet": (
                    meta["qty"] / pallets_with_sku if pallets_with_sku else 0
                ),
                "pallet_layout": meta["pallet_layout"],
                "max_cargo_weight_per_pallet": max_cargo_weight,
                "mixed_pallets": pallets_with_sku,
                "effective_layer_capacity": meta["effective_layer_capacity"],
            }
        )

    return results, mixed_pallets


def create_excel_report(
    selected_container: str,
    container: Dict[str, float],
    results: List[Dict[str, float]],
    mixed_pallets: List[Dict[str, object]],
    total_boxes: int,
    total_cbm: float,
    total_cargo_weight: float,
    total_pallets: int,
    total_pallet_weight: float,
    total_weight: float,
    base_pallet_capacity: int,
    effective_pallet_capacity: int,
    pallet_layout: str,
    cbm_rate: float,
    is_cbm_ok: bool,
    is_weight_ok: bool,
    is_pallet_ok: bool,
    is_double_stack: bool,
    safety_margin: int,
    pallet_l: int,
    pallet_w: int,
    pallet_height: int,
    pallet_weight: float,
    max_stack_height: int,
    pallet_max_load: float,
) -> bytes:
    """시뮬레이션 결과를 여러 시트의 XLSX 파일로 생성합니다."""
    output = BytesIO()

    overall_ok = is_cbm_ok and is_weight_ok and is_pallet_ok and total_boxes > 0

    summary_df = pd.DataFrame(
        [
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
        ],
        columns=["항목", "값"],
    )

    sku_rows = []
    for item in results:
        if item["boxes"] > 0:
            sku_rows.append(
                {
                    "SKU/품목명": item["name"],
                    "박스 수량": int(item["boxes"]),
                    "필요 파레트 수": int(item["pallets"]),
                    "박스 CBM": round(item["cbm"], 3),
                    "화물중량(kg)": round(item["cargo_weight"], 2),
                    "파레트당 1층 수량": int(item["layer_capacity"]),
                    "적재 층수": int(item["layers"]),
                    "기하학적 파레트당 최대 수량": int(
                        item["boxes_per_pallet_geometry"]
                    ),
                    "최종 파레트당 적용 수량": int(item["boxes_per_pallet"]),
                    "파레트 배치 방향": item["pallet_layout"],
                    "파레트당 허용 화물중량(kg)": round(
                        item["max_cargo_weight_per_pallet"], 2
                    ),
                }
            )
    sku_df = pd.DataFrame(sku_rows)

    input_df = pd.DataFrame(
        [
            ["컨테이너 내경(mm)", f"{container['length']} × {container['width']} × {container['height']}"],
            ["파레트 규격(mm)", f"{pallet_l} × {pallet_w} × {pallet_height}"],
            ["빈 파레트 중량(kg)", pallet_weight],
            ["파레트 1개 총 적재 제한 높이(mm)", max_stack_height],
            ["파레트 1개 최대 총중량(kg)", pallet_max_load],
            ["2단 적재", "적용" if is_double_stack else "미적용"],
            ["파레트 수용량 안전 마진(%)", safety_margin],
            ["컨테이너 바닥 파레트 배치", pallet_layout],
            ["컨테이너 바닥 기본 수용량", base_pallet_capacity],
        ],
        columns=["입력/계산 항목", "값"],
    )

    checks_df = pd.DataFrame(
        [
            ["이론 CBM 한도", "적합" if is_cbm_ok else "초과"],
            ["총중량 한도", "적합" if is_weight_ok else "초과"],
            ["파레트 수용량 한도", "적합" if is_pallet_ok else "초과"],
            ["전체 판정", "적합" if overall_ok else "검토 필요"],
        ],
        columns=["검토 항목", "결과"],
    )

    mixed_rows = []
    for pallet_no, pallet in enumerate(mixed_pallets, start=1):
        for layer_no, layer in enumerate(pallet["layers"], start=1):
            mixed_rows.append(
                {
                    "공용 파렛트 번호": pallet_no,
                    "층 번호": layer_no,
                    "SKU/품목명": layer["sku_name"],
                    "해당 층 박스 수량": int(layer["boxes"]),
                    "박스 높이(mm)": layer["height"],
                    "층 화물중량(kg)": round(layer["cargo_weight"], 2),
                    "파렛트 누적 높이(mm)": sum(
                        previous["height"]
                        for previous in pallet["layers"][:layer_no]
                    ),
                }
            )
    mixed_df = pd.DataFrame(mixed_rows)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="종합 결과", index=False)
        sku_df.to_excel(writer, sheet_name="SKU별 상세", index=False)
        mixed_df.to_excel(writer, sheet_name="혼재 파렛트 배치", index=False)
        input_df.to_excel(writer, sheet_name="입력 조건", index=False)
        checks_df.to_excel(writer, sheet_name="판정 체크", index=False)

        for worksheet in writer.book.worksheets:
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for column_cells in worksheet.columns:
                max_length = max(
                    len(str(cell.value)) if cell.value is not None else 0
                    for cell in column_cells
                )
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(
                    max(max_length + 2, 12), 42
                )

    return output.getvalue()


with st.form("mixed_simulation_form"):
    st.subheader("1. 3개 품목(SKU) 규격 및 선적 목표 수량")

    sku_col1, sku_col2, sku_col3 = st.columns(3)

    with sku_col1:
        st.markdown("#### 📦 품목 1 (SKU A)")
        name_1 = st.text_input("품목 1 이름", value="프리미엄 크림")
        l1 = st.number_input("박스 길이 (mm)", min_value=0, value=400, key="l1")
        w1 = st.number_input("박스 너비 (mm)", min_value=0, value=300, key="w1")
        h1 = st.number_input("박스 높이 (mm)", min_value=0, value=250, key="h1")
        wt1 = st.number_input(
            "박스 1개 무게 (kg)",
            min_value=0.0,
            value=15.0,
            format="%.2f",
            key="wt1",
        )
        qty_1 = st.number_input(
            "선적 목표 박스 수량",
            min_value=0,
            value=300,
            step=1,
            key="qty1",
        )

    with sku_col2:
        st.markdown("#### 📦 품목 2 (SKU B)")
        name_2 = st.text_input("품목 2 이름", value="기능성 앰플")
        l2 = st.number_input("박스 길이 (mm)", min_value=0, value=0, key="l2")
        w2 = st.number_input("박스 너비 (mm)", min_value=0, value=0, key="w2")
        h2 = st.number_input("박스 높이 (mm)", min_value=0, value=0, key="h2")
        wt2 = st.number_input(
            "박스 1개 무게 (kg)",
            min_value=0.0,
            value=0.0,
            format="%.2f",
            key="wt2",
        )
        qty_2 = st.number_input(
            "선적 목표 박스 수량",
            min_value=0,
            value=0,
            step=1,
            key="qty2",
        )

    with sku_col3:
        st.markdown("#### 📦 품목 3 (SKU C)")
        name_3 = st.text_input("품목 3 이름", value="마스크팩 세트")
        l3 = st.number_input("박스 길이 (mm)", min_value=0, value=0, key="l3")
        w3 = st.number_input("박스 너비 (mm)", min_value=0, value=0, key="w3")
        h3 = st.number_input("박스 높이 (mm)", min_value=0, value=0, key="h3")
        wt3 = st.number_input(
            "박스 1개 무게 (kg)",
            min_value=0.0,
            value=0.0,
            format="%.2f",
            key="wt3",
        )
        qty_3 = st.number_input(
            "선적 목표 박스 수량",
            min_value=0,
            value=0,
            step=1,
            key="qty3",
        )

    st.divider()

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("2. 파레트 옵션")
        pallet_l = st.number_input("파레트 길이 (mm)", min_value=1, value=1100)
        pallet_w = st.number_input("파레트 너비 (mm)", min_value=1, value=1100)
        pallet_height = st.number_input("빈 파레트 높이 (mm)", min_value=1, value=150)
        pallet_weight = st.number_input(
            "빈 파레트 무게 (kg)",
            min_value=0.1,
            value=20.0,
            format="%.2f",
        )
        max_stack_height = st.number_input(
            "파레트 1개당 총 적재 제한 높이 (mm)",
            min_value=1,
            value=1600,
        )
        pallet_max_load = st.number_input(
            "파레트 1개당 최대 총중량 (kg)",
            min_value=1.0,
            value=1000.0,
            format="%.2f",
            help="박스 화물중량과 빈 파레트 중량을 합친 값의 한도입니다.",
        )

    with col_p2:
        st.subheader("3. 컨테이너 및 적재 방식")
        selected_container = st.selectbox(
            "타겟 컨테이너 종류",
            list(CONTAINER_SPECS.keys()),
        )
        is_double_stack = st.checkbox(
            "🔄 파레트 2단 적재(Double Stacking)",
            value=False,
            help="파레트 1개당 총높이의 2배가 컨테이너 내부 높이 이하여야 합니다.",
        )
        safety_margin = st.slider(
            "파레트 수용량 안전 마진 (%)",
            min_value=0,
            max_value=20,
            value=5,
        )

    submitted = st.form_submit_button("🚀 혼재 적재 시뮬레이션 실행")


if submitted:
    container = CONTAINER_SPECS[selected_container]

    if pallet_l > container["length"] and pallet_l > container["width"]:
        st.error("❌ 파레트 길이가 컨테이너 폭과 길이에 모두 맞지 않습니다.")
        st.stop()

    if pallet_w > container["length"] and pallet_w > container["width"]:
        st.error("❌ 파레트 너비가 컨테이너 폭과 길이에 모두 맞지 않습니다.")
        st.stop()

    single_height_ok = max_stack_height <= container["height"]
    double_height_ok = (
        not is_double_stack
        or max_stack_height * 2 <= container["height"]
    )

    if not single_height_ok:
        st.error(
            f"❌ 파레트 1개 총높이({max_stack_height:,}mm)가 "
            f"컨테이너 내부 높이({container['height']:,}mm)를 초과합니다."
        )
        st.stop()

    if is_double_stack and not double_height_ok:
        st.error(
            f"❌ 2단 적재 불가: 파레트 총높이 2개 층 "
            f"{max_stack_height * 2:,}mm가 컨테이너 내부 높이 "
            f"{container['height']:,}mm를 초과합니다."
        )
        st.stop()

    try:
        sku_inputs = [
            (name_1, l1, w1, h1, wt1, qty_1),
            (name_2, l2, w2, h2, wt2, qty_2),
            (name_3, l3, w3, h3, wt3, qty_3),
        ]

        results, mixed_pallets = calculate_mixed_pallet_plan(
            sku_inputs=sku_inputs,
            pallet_l=pallet_l,
            pallet_w=pallet_w,
            pallet_height=pallet_height,
            pallet_weight=pallet_weight,
            max_stack_height=max_stack_height,
            pallet_max_load=pallet_max_load,
        )
    except ValueError as exc:
        st.error(f"❌ 입력값 검증 오류: {exc}")
        st.stop()

    total_boxes = sum(item["boxes"] for item in results)
    total_cbm = sum(item["cbm"] for item in results)
    total_cargo_weight = sum(item["cargo_weight"] for item in results)
    total_pallets = len(mixed_pallets)
    total_pallet_weight = total_pallets * pallet_weight
    total_weight = total_cargo_weight + total_pallet_weight

    base_pallet_capacity, pallet_layout = get_floor_pallet_capacity(
        container["length"],
        container["width"],
        pallet_l,
        pallet_w,
    )

    physical_pallet_capacity = base_pallet_capacity
    if is_double_stack:
        physical_pallet_capacity *= 2

    effective_pallet_capacity = math.floor(
        physical_pallet_capacity * (1 - safety_margin / 100)
    )

    is_cbm_ok = total_cbm <= container["cbm"]
    is_weight_ok = total_weight <= container["max_payload"]
    is_pallet_ok = total_pallets <= effective_pallet_capacity
    is_all_zero = total_boxes == 0

    st.divider()
    st.subheader(f"📊 [{selected_container}] 시뮬레이션 결과")

    col_res1, col_res2, col_res3 = st.columns(3)

    with col_res1:
        st.markdown("#### 📦 품목별 계산")
        for item in results:
            if item["boxes"] > 0:
                st.write(
                    f"- **{item['name']}**: "
                    f"{int(item['boxes']):,}박스 / "
                    f"{int(item['pallets']):,}파레트"
                )
        st.write(f"- **총 박스 수**: **{total_boxes:,}개**")

    with col_res2:
        st.markdown("#### 🚢 공간 및 파레트")
        st.write(
            f"- 필요 파레트: **{total_pallets:,}개** "
            f"(안전 마진 반영 한도: {effective_pallet_capacity:,}개)"
        )
        st.write(
            f"- 컨테이너 바닥 배치: {base_pallet_capacity:,}개 "
            f"({pallet_layout})"
        )
        st.write(f"- 이론 화물 CBM: **{total_cbm:.2f} CBM**")
        st.write(f"- 컨테이너 명목 용량: {container['cbm']:.2f} CBM")
        cbm_rate = (total_cbm / container["cbm"] * 100) if container["cbm"] else 0
        st.write(f"- 이론 CBM 비율: **{cbm_rate:.1f}%**")

    with col_res3:
        st.markdown("#### ⚖️ 중량 및 높이")
        st.write(f"- 화물 순중량: {total_cargo_weight:,.2f} kg")
        st.write(f"- 파레트 총중량: {total_pallet_weight:,.2f} kg")
        st.write(f"- **총 선적중량**: **{total_weight:,.2f} kg**")
        st.write(f"- 허용 화물중량: {container['max_payload']:,} kg")
        st.write(f"- 파레트 1개 총높이: {max_stack_height:,} mm")
        if is_double_stack:
            st.write(f"- 2단 적재 총높이: {max_stack_height * 2:,} mm")

    if total_boxes > 0:
        with st.expander("SKU별 상세 적재 계산"):
            for item in results:
                if item["boxes"] > 0:
                    st.markdown(f"**{item['name']}**")
                    st.write(
                        f"1층 {int(item['layer_capacity']):,}개 × "
                        f"{int(item['layers']):,}층 = "
                        f"기하학적 최대 {int(item['boxes_per_pallet_geometry']):,}개/전용 파레트 기준"
                    )
                    st.write(
                        f"혼재 파렛트 수: **{int(item['mixed_pallets']):,}개**, "
                        f"평균 박스 수량: **{item['boxes_per_pallet']:.1f}개/파렛트** "
                        f"({item['pallet_layout']})"
                    )

        with st.expander("공용 파렛트별 혼재 배치"):
            for pallet_no, pallet in enumerate(mixed_pallets, start=1):
                layer_text = " / ".join(
                    f"{layer['sku_name']} {int(layer['boxes']):,}박스"
                    for layer in pallet["layers"]
                )
                st.write(
                    f"- **공용 파렛트 {pallet_no}**: {layer_text} "
                    f"(높이 {pallet['height']:,}mm, "
                    f"화물중량 {pallet['cargo_weight']:,.2f}kg)"
                )

        excel_report = create_excel_report(
            selected_container=selected_container,
            container=container,
            results=results,
            mixed_pallets=mixed_pallets,
            total_boxes=total_boxes,
            total_cbm=total_cbm,
            total_cargo_weight=total_cargo_weight,
            total_pallets=total_pallets,
            total_pallet_weight=total_pallet_weight,
            total_weight=total_weight,
            base_pallet_capacity=base_pallet_capacity,
            effective_pallet_capacity=effective_pallet_capacity,
            pallet_layout=pallet_layout,
            cbm_rate=cbm_rate,
            is_cbm_ok=is_cbm_ok,
            is_weight_ok=is_weight_ok,
            is_pallet_ok=is_pallet_ok,
            is_double_stack=is_double_stack,
            safety_margin=safety_margin,
            pallet_l=pallet_l,
            pallet_w=pallet_w,
            pallet_height=pallet_height,
            pallet_weight=pallet_weight,
            max_stack_height=max_stack_height,
            pallet_max_load=pallet_max_load,
        )

        st.download_button(
            label="📥 시뮬레이션 결과 엑셀 다운로드",
            data=excel_report,
            file_name="mixed_loading_simulation_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.divider()
    st.markdown("### 🚦 최종 검토 결과")

    if is_all_zero:
        st.warning("⚠️ 선적 수량이 모두 0개입니다.")
    elif is_cbm_ok and is_weight_ok and is_pallet_ok:
        st.success(
            "✅ 입력 조건 기준으로 이론 CBM, 총중량, 파레트 수용량 및 "
            "높이 조건을 모두 만족합니다."
        )
    else:
        st.error("❌ 현재 입력 조건에서는 선적 적합 판정을 충족하지 못합니다.")
        if not is_cbm_ok:
            st.warning(f"부피 초과: {total_cbm:.2f} CBM > {container['cbm']:.2f} CBM")
        if not is_weight_ok:
            st.warning(f"중량 초과: {total_weight:,.2f} kg > {container['max_payload']:,} kg")
        if not is_pallet_ok:
            st.warning(f"파레트 수량 초과: {total_pallets:,}개 > {effective_pallet_capacity:,}개")