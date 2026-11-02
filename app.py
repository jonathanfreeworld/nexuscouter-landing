import streamlit as st
import math
from chapters import CATEGORIES, CHAPTERS, DEADLINES

st.set_page_config(page_title="K-뷰티·K-푸드 수출 가이드", page_icon="📦", layout="wide")

st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a, #2563eb); padding: 1.8rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <h1 style="margin: 0; font-size: 1.9rem; font-weight: 700;">📦 K-뷰티·K-푸드 해외영업·수출마케팅 가이드</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
            일본 · 미국 · 동남아 · 유럽 | 기준일: 2026.10.29 | 규제와 관세는 수시로 변경되니 거래 전 반드시 최신 내용을 확인하세요.
        </p>
    </div>
""", unsafe_allow_html=True)

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
