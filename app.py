import html
import math

import streamlit as st

import chapters

# ------------------------------------------------------------
# 페이지 설정: 와이드 레이아웃 (양쪽 여백 최소화)
# ------------------------------------------------------------
st.set_page_config(
    page_title="K-푸드·K-뷰티 수출 컨설팅 실행 프레임워크",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# 콘텐츠 불러오기 (누락 시 기본값)
# ------------------------------------------------------------
guide_title = getattr(chapters, "GUIDE_TITLE", "K-푸드·K-뷰티 수출 컨설팅 실행 프레임워크")
guide_subtitle = getattr(chapters, "GUIDE_SUBTITLE", "")
guide_version = getattr(chapters, "GUIDE_VERSION", "")
guide_positioning = getattr(chapters, "GUIDE_POSITIONING", "")

CATEGORIES = getattr(chapters, "CATEGORIES", {})
CHAPTERS = getattr(chapters, "CHAPTERS", [])
DEADLINES = getattr(chapters, "DEADLINES", [])
ROADMAP = getattr(chapters, "ROADMAP", [])
AI_CAPABILITY_MAP = getattr(chapters, "AI_CAPABILITY_MAP", [])
AI_GUARDRAILS = getattr(chapters, "AI_GUARDRAILS", [])
SOURCE_DOCUMENTS = getattr(chapters, "SOURCE_DOCUMENTS", [])

NUM_COLS = 3
TITLE_BY_NO = {c["no"]: c["title"] for c in CHAPTERS}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def split_columns(items, n=NUM_COLS):
    """위에서 아래로 읽히도록 순서대로 n개 열에 나눈다 (1열: 앞쪽, 3열: 뒤쪽)."""
    if not items:
        return [[] for _ in range(n)]
    size = math.ceil(len(items) / n)
    return [items[i * size:(i + 1) * size] for i in range(n)]


def label(text):
    st.markdown(f'<div class="sec-label">{esc(text)}</div>', unsafe_allow_html=True)


def bullets(items):
    st.markdown("\n".join(f"- {x}" for x in items))


# ------------------------------------------------------------
# 스타일
# ------------------------------------------------------------
st.markdown(
    """
<style>
.block-container {
    max-width: 1600px;
    padding-top: 1rem;
    padding-bottom: 1.5rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    line-height: 1.5 !important;
    margin-bottom: 0.3rem !important;
}
[data-testid="stMarkdownContainer"] ul,
[data-testid="stMarkdownContainer"] ol {
    margin-top: 0.15rem !important;
    margin-bottom: 0.5rem !important;
    padding-left: 1.2rem !important;
}
[data-testid="stVerticalBlock"] { gap: 0.55rem; }
[data-testid="stExpander"] details summary {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
}
[data-testid="stExpander"] details { border-radius: 8px; }
.guide-header h1 { font-size: 1.9rem !important; }
.cat-head {
    margin: 0.4rem 0 0.1rem 0;
    padding: 0.3rem 0.65rem;
    border-left: 4px solid #28618A;
    background: rgba(40, 97, 138, 0.10);
    color: #17365D;
    font-size: 0.86rem;
    font-weight: 700;
    border-radius: 3px;
}
.sec-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: #28618A;
    letter-spacing: 0.02em;
    margin: 0.55rem 0 0.1rem 0;
}
.sec-label.warn { color: #B0442A; }
.meta-line {
    font-size: 0.78rem;
    opacity: 0.75;
    margin: 0.1rem 0 0.3rem 0;
}
@media (prefers-color-scheme: dark) {
    .cat-head { color: #BBD7EE; background: rgba(120, 170, 210, 0.16); }
    .sec-label { color: #8FBCE0; }
    .sec-label.warn { color: #F0907A; }
}
@media (max-width: 640px) {
    .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
    .guide-header h1 { font-size: 1.45rem !important; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 헤더 (HTML은 들여쓰기·빈 줄 없이 이어 붙여야 코드 블록으로 처리되지 않음)
# ------------------------------------------------------------
header_html = (
    '<div class="guide-header" style="background:linear-gradient(135deg,#17365D,#28618A);'
    'padding:1.2rem 1.4rem;border-radius:10px;color:white;margin-bottom:0.6rem;">'
    '<div style="font-size:0.76rem;letter-spacing:0.08em;opacity:0.86;margin-bottom:0.35rem;">'
    "EXPORT CONSULTING FRAMEWORK · K-FOOD · K-BEAUTY</div>"
    f'<h1 style="margin:0;font-weight:700;line-height:1.35;color:white;">{esc(guide_title)}</h1>'
    f'<p style="margin:0.5rem 0 0 0;font-size:0.98rem;line-height:1.5;opacity:0.94;">{esc(guide_subtitle)}</p>'
)
if guide_version:
    header_html += f'<p style="margin:0.45rem 0 0 0;font-size:0.76rem;opacity:0.78;">{esc(guide_version)}</p>'
header_html += "</div>"
st.markdown(header_html, unsafe_allow_html=True)

if guide_positioning:
    st.markdown(guide_positioning)

# ------------------------------------------------------------
# 요약 지표
# ------------------------------------------------------------
total_deliverables = sum(len(c["deliverables"]) for c in CHAPTERS)
m1, m2, m3, m4 = st.columns(4)
m1.metric("실행 단계", f"{len(ROADMAP)}단계")
m2.metric("실행 모듈", f"{len(CHAPTERS)}개")
m3.metric("산출물", f"{total_deliverables}종")
m4.metric("반복 점검 항목", f"{len(DEADLINES)}개")

# ------------------------------------------------------------
# 탭
# ------------------------------------------------------------
tab_work, tab_road, tab_risk, tab_ai = st.tabs(
    ["📋 실행 모듈", "🗺️ 단계별 로드맵", "⚠️ 반복 점검", "🤖 AI 업무 통제"]
)

# ============================================================
# 1) 실행 모듈 (3열, 위→아래 순서)
# ============================================================
with tab_work:
    if not CHAPTERS:
        st.warning("표시할 모듈이 없습니다. chapters.py의 CHAPTERS를 확인하세요.")
    else:
        f1, f2 = st.columns([3, 2])
        with f1:
            keyword = st.text_input(
                "검색",
                placeholder="모듈명·과제·산출물 검색 (예: 견적, 인증, 바이어, 샘플)",
                label_visibility="collapsed",
            ).strip().lower()
        with f2:
            selected_cat = st.selectbox(
                "영역", ["전체 영역"] + list(CATEGORIES.values()),
                label_visibility="collapsed",
            )

        def matches(ch: dict) -> bool:
            if selected_cat != "전체 영역" and CATEGORIES.get(ch["cat"]) != selected_cat:
                return False
            if keyword:
                hay = " ".join(
                    [ch["title"], ch["issue"], ch["decision"], ch["owner"], ch["timing"]]
                    + ch["actions"] + ch["criteria"] + ch["redflags"]
                    + ch["ai_use"] + ch["checklist"] + ch["deliverables"]
                ).lower()
                if keyword not in hay:
                    return False
            return True

        filtered = [c for c in CHAPTERS if matches(c)]
        st.caption(f"{len(CHAPTERS)}개 모듈 중 {len(filtered)}개 표시")

        if not filtered:
            st.info("조건에 맞는 모듈이 없습니다. 검색어나 영역을 바꿔 보세요.")

        cols = st.columns(NUM_COLS, gap="medium")
        for col, items in zip(cols, split_columns(filtered)):
            with col:
                prev_cat = None
                for ch in items:
                    if ch["cat"] != prev_cat:
                        st.markdown(
                            f'<div class="cat-head">{esc(CATEGORIES.get(ch["cat"], ""))}</div>',
                            unsafe_allow_html=True,
                        )
                        prev_cat = ch["cat"]

                    with st.container(border=True):
                        st.markdown(f"**{ch['no']:02d} · {ch['title']}**")
                        st.caption(ch["issue"])
                        st.markdown(
                            f'<div class="meta-line">담당 {esc(ch["owner"])} · 시점 {esc(ch["timing"])}</div>',
                            unsafe_allow_html=True,
                        )

                        with st.expander("의사결정 · 실행 과제 · 산출물"):
                            label("의사결정 사항")
                            st.markdown(ch["decision"])

                            label("실행 과제")
                            st.markdown("\n".join(f"{i}. {s}" for i, s in enumerate(ch["actions"], 1)))

                            label("판단 기준 (진행·보류·중단)")
                            bullets(ch["criteria"])

                            st.markdown('<div class="sec-label warn">위험 신호</div>', unsafe_allow_html=True)
                            bullets(ch["redflags"])

                            label("AI 활용 (사람 검수 지점)")
                            bullets(ch["ai_use"])

                            label("착수 전 점검")
                            done = 0
                            for i, item in enumerate(ch["checklist"]):
                                if st.checkbox(item, key=f"chk_{ch['no']}_{i}"):
                                    done += 1
                            total = len(ch["checklist"])
                            if total:
                                st.progress(done / total, text=f"{done}/{total} 확인")

                            label("산출물")
                            bullets(ch["deliverables"])

# ============================================================
# 2) 단계별 로드맵 (3열)
# ============================================================
with tab_road:
    st.markdown("#### 착수부터 첫 거래·운영 체계화까지")
    st.caption("기간은 일반적인 예시입니다. 제품·국가·내부 인력에 따라 조정하세요. 각 단계는 '통과 기준'을 충족한 뒤 다음으로 넘어갑니다.")
    if not ROADMAP:
        st.info("등록된 로드맵이 없습니다.")
    else:
        cols = st.columns(NUM_COLS, gap="medium")
        for col, items in zip(cols, split_columns(ROADMAP)):
            with col:
                for ph in items:
                    with st.container(border=True):
                        st.markdown(f"**{ph['phase']}**")
                        st.caption(f"{ph['period']} · {ph['goal']}")
                        label("포함 모듈")
                        st.markdown(
                            "\n".join(
                                f"- {n:02d} {TITLE_BY_NO.get(n, '')}" for n in ph["modules"]
                            )
                        )
                        label("통과 기준")
                        st.markdown(ph["gate"])

# ============================================================
# 3) 반복 점검 (3열)
# ============================================================
with tab_risk:
    st.markdown("#### 선적·거래 전후 반복 확인 항목")
    st.caption(
        "일반 원칙입니다. 실제 기한과 요건은 제품·목적국·거래별로 "
        "공식 기관과 담당 전문가(관세사·포워더·현지 수입자)에게 확인하세요."
    )
    if not DEADLINES:
        st.info("등록된 점검 항목이 없습니다.")
    else:
        cols = st.columns(NUM_COLS, gap="medium")
        for col, items in zip(cols, split_columns(DEADLINES)):
            with col:
                for d in items:
                    with st.container(border=True):
                        st.markdown(f"**{d['title']}**")
                        st.caption(f"시점: {d['status']}")
                        st.markdown(d["note"])
                        st.caption(f"확인처: {d['source']}")

# ============================================================
# 4) AI 업무 통제 (3열)
# ============================================================
with tab_ai:
    st.markdown("#### 수출업무별 AI 적용 영역")
    if not AI_CAPABILITY_MAP:
        st.info("등록된 AI 적용 항목이 없습니다.")
    else:
        cols = st.columns(NUM_COLS, gap="medium")
        for i, item in enumerate(AI_CAPABILITY_MAP):
            with cols[i % NUM_COLS]:
                with st.container(border=True):
                    st.markdown(f"**{item['technology']}**")
                    st.markdown(item["capability"])
                    label("적용 업무")
                    bullets(item["export_use"])
                    if item.get("caution"):
                        st.markdown('<div class="sec-label warn">주의</div>', unsafe_allow_html=True)
                        st.markdown(item["caution"])

    if AI_GUARDRAILS:
        st.markdown("#### AI 업무 통제 기준")
        cols = st.columns(NUM_COLS, gap="medium")
        for i, g in enumerate(AI_GUARDRAILS):
            with cols[i % NUM_COLS]:
                with st.container(border=True):
                    st.markdown(f"**{g['title']}**")
                    bullets(g["items"])

# ------------------------------------------------------------
# 출처
# ------------------------------------------------------------
if SOURCE_DOCUMENTS:
    st.divider()
    st.markdown("**참고 자료**")
    for src in SOURCE_DOCUMENTS:
        st.markdown(f"- {src}")
