import streamlit as st
import chapters

from chapters import CATEGORIES, CHAPTERS, DEADLINES

# ------------------------------------------------------------
# 페이지 기본 설정
# ------------------------------------------------------------
st.set_page_config(
    page_title="K-푸드·K-뷰티 글로벌 수출 컨설팅 가이드",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 가이드 메타정보

guide_title = getattr(
    chapters,
    "GUIDE_TITLE",
    "K-푸드·K-뷰티 글로벌 사업개발과 수출 컨설팅 가이드",
)
guide_subtitle = getattr(
    chapters,
    "GUIDE_SUBTITLE",
    "시장 진입 전략부터 규제 대응, 바이어 발굴, 거래 실행과 현지 유통까지",
)
guide_version = getattr(chapters, "GUIDE_VERSION", "콘텐츠 버전 확인 필요")
guide_positioning = getattr(chapters, "GUIDE_POSITIONING", "")

# ------------------------------------------------------------
# 모바일 우선 스타일
# 본문 행간 1.5, 문단 및 요소 간 여백 축소
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        max-width: 920px;
        padding-top: 1.15rem;
        padding-bottom: 1.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        line-height: 1.5 !important;
        margin-bottom: 0.35rem !important;
    }
    [data-testid="stMarkdownContainer"] ul,
    [data-testid="stMarkdownContainer"] ol {
        margin-top: 0.2rem !important;
        margin-bottom: 0.55rem !important;
        padding-left: 1.25rem !important;
    }
    [data-testid="stVerticalBlock"] {
        gap: 0.65rem;
    }
    [data-testid="stExpander"] details summary {
        padding-top: 0.65rem;
        padding-bottom: 0.65rem;
    }
    [data-testid="stExpander"] details {
        border-radius: 9px;
    }
    h1, h2, h3 {
        line-height: 1.35 !important;
    }
    @media (max-width: 640px) {
        .block-container {
            padding-top: 0.75rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }
        h1 {
            font-size: 1.55rem !important;
        }
        h2 {
            font-size: 1.25rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 상단 헤더
# ------------------------------------------------------------
st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, #17365D, #28618A);
        padding: 1.35rem 1.25rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 0.8rem;
