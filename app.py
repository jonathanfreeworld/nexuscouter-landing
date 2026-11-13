import streamlit as st
import chapters

from chapters import CATEGORIES, CHAPTERS, DEADLINES

# ------------------------------------------------------------
# 페이지 기본 설정
# ------------------------------------------------------------
st.set_page_config(
    page_title="K-뷰티·K-푸드 수출 가이드",
    page_icon="📦",
    layout="wide",
)

# 가이드 메타정보는 chapters.py에 값이 있을 때 사용한다.
guide_title = getattr(chapters, "GUIDE_TITLE", "K-뷰티·K-푸드 글로벌 수출 실무 가이드")
guide_subtitle = getattr(
    chapters,
    "GUIDE_SUBTITLE",
    "시장검증부터 규제·바이어·거래 실행·재구매까지 연결하는 실무 가이드",
)
guide_version = getattr(chapters, "GUIDE_VERSION", "콘텐츠 버전 확인 필요")

# ------------------------------------------------------------
# 상단 헤더
# ------------------------------------------------------------
st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, #1e3a8a, #2563eb);
        padding: 1.8rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    ">
        <div style="font-size:0.82rem; opacity:0.85; margin-bottom:0.45rem;">
            K-FOOD · K-BEAUTY EXPORT PRACTICE
        </div>
        <h1 style="margin:0; font-size:1.85rem; font-weight:700;">
            {guide_title}
        </h1>
        <p style="margin:0.65rem 0 0 0; font-size:1rem; opacity:0.92;">
            {guide_subtitle}
        </p>
        <p style="margin:0.55rem 0 0 0; font-size:0.8rem; opacity:0.78;">
            {guide_version} · 규제·관세·인증 정보는 거래 전 공식기관을 통해 재확인해야 한다.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 주요 확인사항
# DEADLINES가 문자열 목록 또는 딕셔너리 목록인 두 형식 모두 처리
# ------------------------------------------------------------
st.subheader("거래 전 확인해야 할 주요 항목")

if DEADLINES:
    deadline_cols = st.columns(min(2, len(DEADLINES)))
    for idx, item in enumerate(DEADLINES):
        with deadline_cols[idx % len(deadline_cols)]:
            if isinstance(item, dict):
                title = item.get("title", "확인 항목")
                status = item.get("status", "확인 필요")
                note = item.get("note", "")
                source = item.get("source", "")
                with st.container(border=True):
                    st.markdown(f"**{title}**")
                    st.caption(status)
                    if note:
                        st.write(note)
                    if source:
                        st.caption(f"확인 출처: {source}")
            else:
                st.info(str(item))
else:
    st.info("등록된 확인 항목이 없다. chapters.py의 DEADLINES를 확인한다.")

st.divider()

# ------------------------------------------------------------
# 검색 및 카테고리
# ------------------------------------------------------------
st.subheader("수출 실무 콘텐츠")

category_labels = ["전체"] + list(CATEGORIES.values())
selected_category = st.radio(
    "카테고리",
    category_labels,
    horizontal=True,
    label_visibility="collapsed",
)

search_query = st.text_input(
