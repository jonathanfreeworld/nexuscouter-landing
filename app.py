import html

import streamlit as st

import chapters

# ------------------------------------------------------------
# 페이지 기본 설정 (반드시 다른 st 호출보다 먼저)
# ------------------------------------------------------------
st.set_page_config(
    page_title="K-푸드·K-뷰티 글로벌 수출 컨설팅 가이드",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# 콘텐츠 불러오기 (누락 시 기본값 사용)
# ------------------------------------------------------------
guide_title = getattr(
    chapters, "GUIDE_TITLE",
    "K-푸드·K-뷰티 글로벌 사업개발과 수출 컨설팅 가이드",
)
guide_subtitle = getattr(
    chapters, "GUIDE_SUBTITLE",
    "시장 진입 전략부터 규제 대응, 바이어 발굴, 거래 실행과 현지 유통까지",
)
guide_version = getattr(chapters, "GUIDE_VERSION", "")
guide_positioning = getattr(chapters, "GUIDE_POSITIONING", "")

CATEGORIES = getattr(chapters, "CATEGORIES", {})
CHAPTERS = getattr(chapters, "CHAPTERS", [])
DEADLINES = getattr(chapters, "DEADLINES", [])
AI_CAPABILITY_MAP = getattr(chapters, "AI_CAPABILITY_MAP", [])
SOURCE_DOCUMENTS = getattr(chapters, "SOURCE_DOCUMENTS", [])


def esc(value) -> str:
    """HTML 삽입용 이스케이프."""
    return html.escape(str(value), quote=True)


# ------------------------------------------------------------
# 모바일 우선 스타일
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
[data-testid="stVerticalBlock"] { gap: 0.65rem; }
[data-testid="stExpander"] details summary {
    padding-top: 0.65rem;
    padding-bottom: 0.65rem;
}
[data-testid="stExpander"] details { border-radius: 9px; }
h1, h2, h3 { line-height: 1.35 !important; }
.guide-header h1 { font-size: 1.8rem !important; }
.cat-chip {
    display: inline-block;
    padding: 0.1rem 0.6rem;
    border-radius: 999px;
    background: rgba(40, 97, 138, 0.14);
    color: #28618A;
    font-size: 0.78rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
}
@media (max-width: 640px) {
    .block-container {
        padding-top: 0.75rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
    .guide-header h1 { font-size: 1.45rem !important; }
    h2 { font-size: 1.25rem !important; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 상단 헤더
# 주의: st.markdown 안의 HTML은 들여쓰기 4칸 이상 / 빈 줄이 있으면
#       코드 블록으로 처리되므로 한 줄씩 이어 붙여서 만든다.
# ------------------------------------------------------------
header_html = (
    '<div class="guide-header" style="background:linear-gradient(135deg,#17365D,#28618A);'
    'padding:1.35rem 1.25rem;border-radius:10px;color:white;margin-bottom:0.8rem;">'
    '<div style="font-size:0.78rem;letter-spacing:0.08em;opacity:0.86;margin-bottom:0.4rem;">'
    "EXPORT BUSINESS CONSULTING · K-FOOD · K-BEAUTY</div>"
    f'<h1 style="margin:0;font-weight:700;line-height:1.35;color:white;">{esc(guide_title)}</h1>'
    f'<p style="margin:0.55rem 0 0 0;font-size:0.98rem;line-height:1.5;opacity:0.94;">{esc(guide_subtitle)}</p>'
)
if guide_version:
    header_html += (
        f'<p style="margin:0.55rem 0 0 0;font-size:0.78rem;opacity:0.78;">{esc(guide_version)}</p>'
    )
header_html += "</div>"

st.markdown(header_html, unsafe_allow_html=True)

if guide_positioning:
    st.markdown(guide_positioning)

# ------------------------------------------------------------
# 탭 구성
# ------------------------------------------------------------
tab_guide, tab_deadline, tab_ai = st.tabs(
    ["📘 장별 가이드", "🗓️ 점검 일정", "🤖 AI 활용 지도"]
)

# ============================================================
# 1) 장별 가이드
# ============================================================
with tab_guide:
    if not CHAPTERS:
        st.warning("표시할 장 데이터가 없습니다. chapters.py의 CHAPTERS를 확인하세요.")
    else:
        keyword = st.text_input(
            "검색",
            placeholder="장 제목, 요약, 산출물 등으로 검색",
            label_visibility="collapsed",
        ).strip().lower()

        cat_options = ["전체"] + [CATEGORIES[k] for k in CATEGORIES]
        selected_cat = st.selectbox("분야 선택", cat_options)

        def matches(ch: dict) -> bool:
            if selected_cat != "전체":
                if CATEGORIES.get(ch["cat"]) != selected_cat:
                    return False
            if keyword:
                haystack = " ".join(
                    [
                        ch["title"], ch["summary"], ch["learning_goal"], ch["body"],
                        " ".join(ch["steps"]), " ".join(ch["points"]),
                        " ".join(ch["checklist"]), " ".join(ch["deliverables"]),
                    ]
                ).lower()
                if keyword not in haystack:
                    return False
            return True

        filtered = [ch for ch in CHAPTERS if matches(ch)]
        st.caption(f"총 {len(CHAPTERS)}개 장 중 {len(filtered)}개 표시")

        if not filtered:
            st.info("조건에 맞는 장이 없습니다. 검색어나 분야를 바꿔 보세요.")

        for ch in filtered:
            label = f"{ch['no']:02d}. {ch['title']}"
            with st.expander(label):
                cat_name = CATEGORIES.get(ch["cat"], "")
                if cat_name:
                    st.markdown(
                        f'<span class="cat-chip">{esc(cat_name)}</span>',
                        unsafe_allow_html=True,
                    )

                st.markdown(f"**핵심 요약**  \n{ch['summary']}")
                st.markdown(f"**학습 목표**  \n{ch['learning_goal']}")
                st.markdown(f"**주요 내용**  \n{ch['body']}")

                st.markdown("**업무 단계**")
                st.markdown(
                    "\n".join(f"{i}. {s}" for i, s in enumerate(ch["steps"], start=1))
                )

                st.markdown("**실무 포인트**")
                st.markdown("\n".join(f"- {p}" for p in ch["points"]))

                st.markdown("**점검 체크리스트**")
                done = 0
                for i, item in enumerate(ch["checklist"]):
                    if st.checkbox(item, key=f"chk_{ch['no']}_{i}"):
                        done += 1
                total = len(ch["checklist"])
                if total:
                    st.progress(done / total, text=f"완료 {done}/{total}")

                st.markdown("**산출물**")
                st.markdown("\n".join(f"- {d}" for d in ch["deliverables"]))

# ============================================================
# 2) 점검 일정
# ============================================================
with tab_deadline:
    st.markdown("#### 수출 진행 중 반복 확인할 항목")
    st.caption(
        "아래 내용은 일반 원칙입니다. 실제 기한과 요건은 제품·목적국·거래별로 "
        "공식 기관과 담당 전문가에게 확인하세요."
    )
    if not DEADLINES:
        st.info("등록된 점검 항목이 없습니다.")
    for d in DEADLINES:
        with st.container(border=True):
            st.markdown(f"**{d['title']}**")
            st.markdown(f"시점: {d['status']}")
            st.markdown(d["note"])
            st.caption(f"확인처: {d['source']}")

# ============================================================
# 3) AI 활용 지도
# ============================================================
with tab_ai:
    st.markdown("#### 수출업무에 적용 가능한 AI 기술")
    st.caption("AI 산출물은 사실 확인과 담당자 승인을 거친 뒤 사용하세요.")
    if not AI_CAPABILITY_MAP:
        st.info("등록된 AI 활용 항목이 없습니다.")
    for item in AI_CAPABILITY_MAP:
        with st.container(border=True):
            st.markdown(f"**{item['technology']}**")
            st.markdown(item["capability"])
            st.markdown(
                "활용 예시\n" + "\n".join(f"- {u}" for u in item["export_use"])
            )

# ------------------------------------------------------------
# 하단 출처
# ------------------------------------------------------------
if SOURCE_DOCUMENTS:
    st.divider()
    st.markdown("**참고 자료**")
    for src in SOURCE_DOCUMENTS:
        st.markdown(f"- {src}")
