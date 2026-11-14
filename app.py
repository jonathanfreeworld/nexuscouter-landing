import html
import math

import streamlit as st

import chapters

# ------------------------------------------------------------
# 페이지 설정: 와이드 레이아웃
# ------------------------------------------------------------
st.set_page_config(
    page_title="K-푸드·K-뷰티 AI 수출 실행 플레이북",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# 콘텐츠 불러오기 (누락 시 기본값)
# ------------------------------------------------------------
guide_title = getattr(chapters, "GUIDE_TITLE", "K-푸드·K-뷰티 AI 수출 실행 플레이북")
guide_subtitle = getattr(chapters, "GUIDE_SUBTITLE", "")
guide_version = getattr(chapters, "GUIDE_VERSION", "")
guide_positioning = getattr(chapters, "GUIDE_POSITIONING", "")

CATEGORIES = getattr(chapters, "CATEGORIES", {})
CHAPTERS = getattr(chapters, "CHAPTERS", [])
ROADMAP = getattr(chapters, "ROADMAP", [])
TOOLS = getattr(chapters, "TOOLS", [])
CHECKLISTS = getattr(chapters, "CHECKLISTS", [])
DEADLINES = getattr(chapters, "DEADLINES", [])
TROUBLESHOOTING = getattr(chapters, "TROUBLESHOOTING", [])
AI_GUARDRAILS = getattr(chapters, "AI_GUARDRAILS", [])
SOURCE_DOCUMENTS = getattr(chapters, "SOURCE_DOCUMENTS", [])

NUM_COLS = 3
TITLE_BY_NO = {c["no"]: c["title"] for c in CHAPTERS}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def split_columns(items, n=NUM_COLS):
    """위에서 아래로 읽히도록 순서대로 n개 열에 나눈다."""
    if not items:
        return [[] for _ in range(n)]
    size = math.ceil(len(items) / n)
    return [items[i * size:(i + 1) * size] for i in range(n)]


def label(text, warn=False):
    cls = "sec-label warn" if warn else "sec-label"
    st.markdown(f'<div class="{cls}">{esc(text)}</div>', unsafe_allow_html=True)


def bullets(items):
    st.markdown("\n".join(f"- {x}" for x in items))


def numbered(items):
    st.markdown("\n".join(f"{i}. {x}" for i, x in enumerate(items, 1)))


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
    "EXPORT PLAYBOOK · K-FOOD · K-BEAUTY</div>"
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
# 요약 지표 (완료 카드 수는 이전 실행의 체크 상태를 반영)
# ------------------------------------------------------------
done_count = sum(1 for c in CHAPTERS if st.session_state.get(f"done_{c['no']}", False))
total_outputs = sum(len(c["output"]) for c in CHAPTERS)
m1, m2, m3, m4 = st.columns(4)
m1.metric("진행 단계", f"{len(CATEGORIES)}단계")
m2.metric("작업 카드", f"{len(CHAPTERS)}개")
m3.metric("결과물", f"{total_outputs}종")
m4.metric("완료한 카드", f"{done_count}/{len(CHAPTERS)}")

# ------------------------------------------------------------
# 탭
# ------------------------------------------------------------
tab_work, tab_road, tab_tool, tab_check, tab_fix = st.tabs(
    ["📋 작업 카드", "🗺️ 단계별 로드맵", "🧰 도구·서비스", "✅ 점검표", "🔧 막힐 때"]
)

# ============================================================
# 1) 작업 카드 (3열, 위→아래 순서)
# ============================================================
with tab_work:
    if not CHAPTERS:
        st.warning("표시할 카드가 없습니다. chapters.py의 CHAPTERS를 확인하세요.")
    else:
        f1, f2 = st.columns([3, 2])
        with f1:
            keyword = st.text_input(
                "검색",
                placeholder="카드·도구·결과물 검색 (예: 광고, 촬영, 견적, 바이어)",
                label_visibility="collapsed",
            ).strip().lower()
        with f2:
            selected_cat = st.selectbox(
                "단계", ["전체 단계"] + list(CATEGORIES.values()),
                label_visibility="collapsed",
            )

        def matches(ch: dict) -> bool:
            if selected_cat != "전체 단계" and CATEGORIES.get(ch["cat"]) != selected_cat:
                return False
            if keyword:
                hay = " ".join(
                    [ch["title"], ch["goal"], ch["time"], ch["owner"]]
                    + ch["tools"] + ch["prep"] + ch["steps"] + ch["tips"]
                    + ch["mistakes"] + ch["ai"] + ch["output"]
                ).lower()
                if keyword not in hay:
                    return False
            return True

        filtered = [c for c in CHAPTERS if matches(c)]
        st.caption(f"{len(CHAPTERS)}개 카드 중 {len(filtered)}개 표시")

        if not filtered:
            st.info("조건에 맞는 카드가 없습니다. 검색어나 단계를 바꿔 보세요.")

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
                        st.caption(ch["goal"])
                        st.markdown(
                            f'<div class="meta-line">소요 {esc(ch["time"])} · 담당 {esc(ch["owner"])}</div>',
                            unsafe_allow_html=True,
                        )

                        with st.expander("작업 순서 · 팁 · 결과물"):
                            label("쓰는 도구")
                            bullets(ch["tools"])
                            label("준비물")
                            bullets(ch["prep"])
                            label("작업 순서")
                            numbered(ch["steps"])
                            label("현장 팁")
                            bullets(ch["tips"])
                            label("자주 나는 실수", warn=True)
                            bullets(ch["mistakes"])
                            label("AI 활용법")
                            bullets(ch["ai"])
                            label("결과물")
                            bullets(ch["output"])
                            st.checkbox("이 카드 완료", key=f"done_{ch['no']}")

# ============================================================
# 2) 단계별 로드맵 (3열)
# ============================================================
with tab_road:
    st.markdown("#### 착수부터 첫 거래·재주문까지")
    st.caption("기간은 예시이며 단계가 일부 겹칠 수 있습니다. 각 단계의 '넘어가는 조건'을 채운 뒤 다음으로 이동하세요.")
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
                        label("포함 카드")
                        bullets([f"{n:02d} {TITLE_BY_NO.get(n, '')}" for n in ph["modules"]])
                        label("넘어가는 조건")
                        st.markdown(ph["gate"])

# ============================================================
# 3) 도구·서비스 (3열)
# ============================================================
with tab_tool:
    st.markdown("#### 단계별로 쓰는 도구와 서비스")
    st.caption("서비스 명칭·제공 범위·화면은 수시로 바뀝니다. 이용 전에 공식 안내를 확인하세요.")
    if not TOOLS:
        st.info("등록된 도구가 없습니다.")
    else:
        cols = st.columns(NUM_COLS, gap="medium")
        for col, items in zip(cols, split_columns(TOOLS)):
            with col:
                for t in items:
                    with st.container(border=True):
                        st.markdown(f"**{t['name']}**")
                        st.markdown(t["use"])
                        st.caption(f"쓰는 단계: {t['phase']} · 이용: {t['access']}")
                        st.markdown(
                            f'<div class="meta-line">주의 · {esc(t["caution"])}</div>',
                            unsafe_allow_html=True,
                        )

# ============================================================
# 4) 점검표 (체크리스트 + 반복 점검 + AI 규칙)
# ============================================================
with tab_check:
    st.markdown("#### 실행 직전 점검표")
    if CHECKLISTS:
        cols = st.columns(2, gap="medium")
        for i, cl in enumerate(CHECKLISTS):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**{cl['title']}**")
                    st.caption(cl["when"])
                    done = 0
                    for j, item in enumerate(cl["items"]):
                        if st.checkbox(item, key=f"ck_{i}_{j}"):
                            done += 1
                    total = len(cl["items"])
                    st.progress(done / total, text=f"{done}/{total} 확인")

    st.markdown("#### 반복 확인 항목")
    st.caption("일반 원칙입니다. 실제 기한과 요건은 제품·목적국·거래별로 공식 기관과 전문가에게 확인하세요.")
    if DEADLINES:
        cols = st.columns(NUM_COLS, gap="medium")
        for col, items in zip(cols, split_columns(DEADLINES)):
            with col:
                for d in items:
                    with st.container(border=True):
                        st.markdown(f"**{d['title']}**")
                        st.caption(f"시점: {d['status']}")
                        st.markdown(d["note"])
                        st.caption(f"확인처: {d['source']}")

    st.markdown("#### AI 사용 규칙")
    if AI_GUARDRAILS:
        cols = st.columns(NUM_COLS, gap="medium")
        for i, g in enumerate(AI_GUARDRAILS):
            with cols[i % NUM_COLS]:
                with st.container(border=True):
                    st.markdown(f"**{g['title']}**")
                    bullets(g["items"])

# ============================================================
# 5) 막힐 때 처방 (3열)
# ============================================================
with tab_fix:
    st.markdown("#### 이런 증상이면 여기로 돌아가세요")
    if not TROUBLESHOOTING:
        st.info("등록된 처방이 없습니다.")
    else:
        cols = st.columns(NUM_COLS, gap="medium")
        for col, items in zip(cols, split_columns(TROUBLESHOOTING)):
            with col:
                for t in items:
                    with st.container(border=True):
                        st.markdown(f"**{t['symptom']}**")
                        label("원인 후보")
                        bullets(t["causes"])
                        label("돌아갈 카드")
                        bullets([f"{n:02d} {TITLE_BY_NO.get(n, '')}" for n in t["go_to"]])
                        label("처방")
                        st.markdown(t["action"])

# ------------------------------------------------------------
# 참고 자료
# ------------------------------------------------------------
if SOURCE_DOCUMENTS:
    st.divider()
    st.markdown("**참고 자료**")
    for src in SOURCE_DOCUMENTS:
        st.markdown(f"- {src}")
