import html
import math

import streamlit as st

import ai_helper
import chapters

# ------------------------------------------------------------
# 페이지 설정
# ------------------------------------------------------------
st.set_page_config(
    page_title="K-푸드·K-뷰티 AI 수출프로세스",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# 콘텐츠 불러오기
# ------------------------------------------------------------
guide_title = getattr(chapters, "GUIDE_TITLE", "AI 수출 프로세스")
guide_subtitle = getattr(chapters, "GUIDE_SUBTITLE", "")
guide_version = getattr(chapters, "GUIDE_VERSION", "")
guide_positioning = getattr(chapters, "GUIDE_POSITIONING", "")
COMPANY = getattr(chapters, "COMPANY", {})
CATEGORIES = getattr(chapters, "CATEGORIES", {})
CHAPTERS = getattr(chapters, "CHAPTERS", [])
ROADMAP = getattr(chapters, "ROADMAP", [])
TOOLS = getattr(chapters, "TOOLS", [])
CHECKLISTS = getattr(chapters, "CHECKLISTS", [])
DEADLINES = getattr(chapters, "DEADLINES", [])
TROUBLESHOOTING = getattr(chapters, "TROUBLESHOOTING", [])
AI_GUARDRAILS = getattr(chapters, "AI_GUARDRAILS", [])
PROMPT_TASKS = getattr(chapters, "PROMPT_TASKS", [])
COMMON_RULES = getattr(chapters, "COMMON_RULES", "")
PRIVACY_NOTICE = getattr(chapters, "PRIVACY_NOTICE", "")
SOURCE_DOCUMENTS = getattr(chapters, "SOURCE_DOCUMENTS", [])

NUM_COLS = 3
TITLE_BY_NO = {c["no"]: c["title"] for c in CHAPTERS}
TASK_BY_ID = {t["id"]: t for t in PROMPT_TASKS}
TASKS_BY_MODULE = {}
for _t in PROMPT_TASKS:
    for _n in _t.get("related", []):
        TASKS_BY_MODULE.setdefault(_n, []).append(_t)

AI_LIVE = ai_helper.is_enabled()


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


def cta(key, primary=True):
    """회사 상담 연결 버튼 (주소가 비어 있으면 표시하지 않음)."""
    url = COMPANY.get("contact_url", "")
    if url:
        st.link_button(
            COMPANY.get("cta_text", "전문가에게 상담 받기"), url,
            type="primary" if primary else "secondary", use_container_width=True,
        )


# ------------------------------------------------------------
# 스타일 (홈페이지 임베드용으로 Streamlit 기본 UI는 숨김)
# ------------------------------------------------------------
st.markdown(
    """
<style>
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
#MainMenu, footer { display: none !important; visibility: hidden; }
.block-container {
    max-width: 1600px;
    padding-top: 0.8rem;
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
[data-testid="stExpander"] details summary { padding-top: 0.5rem; padding-bottom: 0.5rem; }
[data-testid="stExpander"] details { border-radius: 8px; }
.guide-header h1 { font-size: 1.9rem !important; }
.steps-line { font-size: 0.86rem; opacity: 0.92; margin-top: 0.7rem; }
.cat-head {
    margin: 0.4rem 0 0.1rem 0; padding: 0.3rem 0.65rem;
    border-left: 4px solid #28618A; background: rgba(40, 97, 138, 0.10);
    color: #17365D; font-size: 0.86rem; font-weight: 700; border-radius: 3px;
}
.sec-label {
    font-size: 0.78rem; font-weight: 700; color: #28618A;
    letter-spacing: 0.02em; margin: 0.55rem 0 0.1rem 0;
}
.sec-label.warn { color: #B0442A; }
.meta-line { font-size: 0.78rem; opacity: 0.75; margin: 0.1rem 0 0.3rem 0; }
.col-title { font-size: 1.02rem; font-weight: 700; margin-bottom: 0.2rem; }
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
# 헤더 (HTML은 들여쓰기·빈 줄 없이 이어 붙임)
# ------------------------------------------------------------
company_name = COMPANY.get("name", "")
eyebrow = f"{company_name} · AI EXPORT HELPER" if company_name else "AI EXPORT HELPER · K-FOOD · K-BEAUTY"
header_html = (
    '<div class="guide-header" style="background:linear-gradient(135deg,#17365D,#28618A);'
    'padding:1.2rem 1.4rem;border-radius:10px;color:white;">'
    f'<div style="font-size:0.76rem;letter-spacing:0.08em;opacity:0.86;margin-bottom:0.35rem;">{esc(eyebrow)}</div>'
    f'<h1 style="margin:0;font-weight:700;line-height:1.35;color:white;">{esc(guide_title)}</h1>'
    f'<p style="margin:0.5rem 0 0 0;font-size:0.98rem;line-height:1.5;opacity:0.94;">{esc(guide_subtitle)}</p>'
    '<div class="steps-line">① 하는 일 고르기 &nbsp;→&nbsp; ② 정보 입력 &nbsp;→&nbsp; '
    '③ 완성된 질문을 AI에 붙여 넣기 &nbsp;→&nbsp; ④ 답변 확인 항목 점검</div>'
    "</div>"
)
if COMPANY.get("contact_url"):
    h1, h2 = st.columns([5, 1.1], vertical_alignment="center")
    with h1:
        st.markdown(header_html, unsafe_allow_html=True)
    with h2:
        cta("top")
else:
    st.markdown(header_html, unsafe_allow_html=True)

if guide_positioning:
    st.markdown(guide_positioning)
if PRIVACY_NOTICE:
    st.info(PRIVACY_NOTICE, icon="🔒")

# ------------------------------------------------------------
# 탭
# ------------------------------------------------------------
tab_ai, tab_stage, tab_guide, tab_check, tab_fix, tab_tool = st.tabs(
    ["🤖 AI 도우미", "📍 진행 단계", "📚 상세 가이드", "✅ 점검표", "🔧 막힐 때", "🧰 도구·지원사업"]
)

# ============================================================
# 1) AI 도우미: [업무 선택] [정보 입력] [완성된 질문]
# ============================================================
with tab_ai:
    if not PROMPT_TASKS:
        st.warning("등록된 업무가 없습니다.")
    else:
        if "task_id" not in st.session_state:
            st.session_state.task_id = PROMPT_TASKS[0]["id"]

        def pick(task_id):
            st.session_state.task_id = task_id

        task = TASK_BY_ID.get(st.session_state.task_id, PROMPT_TASKS[0])
        c_list, c_form, c_out = st.columns([1.0, 1.25, 1.75], gap="medium")

        # --- 1열: 업무 선택 ---
        with c_list:
            st.markdown('<div class="col-title">① 무엇을 도와드릴까요?</div>', unsafe_allow_html=True)
            prev_stage = None
            for t in PROMPT_TASKS:
                if t["stage"] != prev_stage:
                    st.markdown(
                        f'<div class="cat-head">{esc(CATEGORIES.get(t["stage"], ""))}</div>',
                        unsafe_allow_html=True,
                    )
                    prev_stage = t["stage"]
                st.button(
                    f"{t['icon']} {t['title']}", key=f"pick_{t['id']}",
                    use_container_width=True,
                    type="primary" if t["id"] == task["id"] else "secondary",
                    on_click=pick, args=(t["id"],),
                )

        # --- 2열: 정보 입력 ---
        values = {}
        with c_form:
            st.markdown(f'<div class="col-title">② {esc(task["icon"])} {esc(task["title"])}</div>', unsafe_allow_html=True)
            st.caption(task["situation"])
            for f in task["fields"]:
                k = f"in_{task['id']}_{f['key']}"
                if f.get("long"):
                    values[f["key"]] = st.text_area(f["label"], key=k, placeholder=f.get("placeholder", ""), height=90)
                else:
                    values[f["key"]] = st.text_input(f["label"], key=k, placeholder=f.get("placeholder", ""))
            st.caption("비워 둔 칸은 질문에 [입력 필요]로 표시됩니다.")

        # --- 3열: 완성된 질문 + 확인 항목 ---
        with c_out:
            prompt_text = ai_helper.build_prompt(task, values, COMMON_RULES)
            st.markdown('<div class="col-title">③ AI에 붙여 넣을 질문</div>', unsafe_allow_html=True)
            st.caption("오른쪽 위의 복사 아이콘을 눌러 ChatGPT·Claude·Gemini 등에 붙여 넣으세요.")
            try:
                st.code(prompt_text, language=None, wrap_lines=True)
            except TypeError:
                st.code(prompt_text, language=None)

            if AI_LIVE:
                calls = st.session_state.get("ai_calls", 0)
                limit = ai_helper.max_calls_per_session()
                if st.button(
                    "✨ 여기서 바로 AI에게 물어보기", key=f"run_{task['id']}",
                    disabled=calls >= limit, use_container_width=True,
                ):
                    try:
                        with st.spinner("AI가 답변을 만드는 중입니다..."):
                            st.session_state[f"ans_{task['id']}"] = ai_helper.ask_ai(prompt_text)
                        st.session_state.ai_calls = calls + 1
                    except Exception as exc:  # 네트워크·키·한도 오류를 사용자 친화적으로 표시
                        st.error(f"AI 응답을 받지 못했습니다. 잠시 후 다시 시도해 주세요. ({type(exc).__name__})")
                if calls >= limit:
                    st.caption("이번 접속에서 사용할 수 있는 횟수를 모두 사용했습니다. 위 질문을 복사해 사용 중인 AI에 붙여 넣어 주세요.")
                answer = st.session_state.get(f"ans_{task['id']}")
                if answer:
                    with st.container(border=True):
                        st.markdown(answer)
                    st.caption("AI 답변은 초안입니다. 아래 '답변 확인 항목'을 점검한 뒤 사용하세요.")

            with st.expander("✅ 답변을 받은 뒤 꼭 확인하세요", expanded=True):
                bullets(task["verify"])
            with st.expander("💡 AI에게 잘 시키는 법"):
                bullets(task["tips"])
            if task.get("expert"):
                st.warning(task["expert"], icon="⚠️")
                cta(f"expert_{task['id']}", primary=False)
            related = task.get("related", [])
            if related:
                st.caption("관련 가이드: " + " · ".join(f"{n:02d} {TITLE_BY_NO.get(n, '')}" for n in related))

# ============================================================
# 2) 진행 단계: 지금 어디쯤이고 무엇을 할지
# ============================================================
with tab_stage:
    st.markdown("#### 지금 어느 단계에 계신가요?")
    if not ROADMAP:
        st.info("등록된 단계가 없습니다.")
    else:
        names = [r["phase"] for r in ROADMAP]
        chosen = st.selectbox("현재 단계", names, label_visibility="collapsed")
        ph = ROADMAP[names.index(chosen)]
        stage_key = next((k for k, v in CATEGORIES.items() if v == ph["phase"]), None)

        s1, s2, s3 = st.columns(3, gap="medium")
        with s1:
            with st.container(border=True):
                st.markdown(f"**{ph['phase']}**")
                st.caption(f"{ph['period']} (예시)")
                st.markdown(ph["goal"])
                label("다음 단계로 넘어가는 조건")
                st.markdown(ph["gate"])
        with s2:
            with st.container(border=True):
                st.markdown("**이 단계에서 할 일**")
                bullets([f"**{TITLE_BY_NO.get(n, '')}** — {next(c['goal'] for c in CHAPTERS if c['no'] == n)}" for n in ph["modules"]])
        with s3:
            with st.container(border=True):
                st.markdown("**AI 도우미로 바로 할 수 있는 일**")
                stage_tasks = [t for t in PROMPT_TASKS if t["stage"] == stage_key]
                if stage_tasks:
                    bullets([f"{t['icon']} {t['title']}" for t in stage_tasks])
                    st.caption("'AI 도우미' 탭에서 같은 이름의 업무를 선택하세요.")
                else:
                    st.caption("이 단계는 상세 가이드의 작업 카드를 참고하세요.")
                cta("stage", primary=False)

        st.markdown("#### 전체 단계 한눈에")
        cols = st.columns(NUM_COLS, gap="medium")
        for col, items in zip(cols, split_columns(ROADMAP)):
            with col:
                for r in items:
                    with st.container(border=True):
                        st.markdown(f"**{r['phase']}**")
                        st.caption(f"{r['period']} · {r['goal']}")
                        bullets([f"{n:02d} {TITLE_BY_NO.get(n, '')}" for n in r["modules"]])

# ============================================================
# 3) 상세 가이드 (작업 카드 3열)
# ============================================================
with tab_guide:
    if not CHAPTERS:
        st.warning("표시할 카드가 없습니다.")
    else:
        f1, f2 = st.columns([3, 2])
        with f1:
            keyword = st.text_input(
                "가이드 검색", placeholder="찾고 싶은 내용 (예: 광고, 촬영, 견적, 바이어)",
                label_visibility="collapsed", key="guide_search",
            ).strip().lower()
        with f2:
            selected_cat = st.selectbox("단계", ["전체 단계"] + list(CATEGORIES.values()),
                                        label_visibility="collapsed", key="guide_cat")

        def matches(ch):
            if selected_cat != "전체 단계" and CATEGORIES.get(ch["cat"]) != selected_cat:
                return False
            if keyword:
                hay = " ".join([ch["title"], ch["goal"], ch["time"], ch["owner"]] + ch["tools"] + ch["prep"]
                               + ch["steps"] + ch["tips"] + ch["mistakes"] + ch["ai"] + ch["output"]).lower()
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
                        st.markdown(f'<div class="cat-head">{esc(CATEGORIES.get(ch["cat"], ""))}</div>',
                                    unsafe_allow_html=True)
                        prev_cat = ch["cat"]
                    with st.container(border=True):
                        st.markdown(f"**{ch['no']:02d} · {ch['title']}**")
                        st.caption(ch["goal"])
                        st.markdown(f'<div class="meta-line">소요 {esc(ch["time"])} · 담당 {esc(ch["owner"])}</div>',
                                    unsafe_allow_html=True)
                        linked = TASKS_BY_MODULE.get(ch["no"], [])
                        if linked:
                            st.markdown("🤖 AI 도우미: " + ", ".join(f"**{t['title']}**" for t in linked))
                        with st.expander("작업 순서 · 팁 · 결과물"):
                            label("쓰는 도구");   bullets(ch["tools"])
                            label("준비물");      bullets(ch["prep"])
                            label("작업 순서");   numbered(ch["steps"])
                            label("현장 팁");     bullets(ch["tips"])
                            label("자주 나는 실수", warn=True); bullets(ch["mistakes"])
                            label("AI 활용법");   bullets(ch["ai"])
                            label("결과물");      bullets(ch["output"])
                            st.checkbox("완료", key=f"done_{ch['no']}")

# ============================================================
# 4) 점검표 + 반복 확인 + AI 사용 규칙
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
                    done = sum(1 for j, item in enumerate(cl["items"]) if st.checkbox(item, key=f"ck_{i}_{j}"))
                    st.progress(done / len(cl["items"]), text=f"{done}/{len(cl['items'])} 확인")

    st.markdown("#### 반복해서 확인할 항목")
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

    st.markdown("#### AI를 쓸 때의 원칙")
    if AI_GUARDRAILS:
        cols = st.columns(NUM_COLS, gap="medium")
        for i, g in enumerate(AI_GUARDRAILS):
            with cols[i % NUM_COLS]:
                with st.container(border=True):
                    st.markdown(f"**{g['title']}**")
                    bullets(g["items"])

# ============================================================
# 5) 막힐 때
# ============================================================
with tab_fix:
    st.markdown("#### 이런 증상이면 여기로 돌아가세요")
    if TROUBLESHOOTING:
        cols = st.columns(NUM_COLS, gap="medium")
        for col, items in zip(cols, split_columns(TROUBLESHOOTING)):
            with col:
                for t in items:
                    with st.container(border=True):
                        st.markdown(f"**{t['symptom']}**")
                        label("원인 후보");   bullets(t["causes"])
                        label("돌아갈 가이드"); bullets([f"{n:02d} {TITLE_BY_NO.get(n, '')}" for n in t["go_to"]])
                        label("처방");        st.markdown(t["action"])
    cta("fix", primary=False)

# ============================================================
# 6) 도구·지원사업
# ============================================================
with tab_tool:
    st.markdown("#### 단계별로 쓰는 도구와 지원사업")
    st.caption("서비스 명칭·제공 범위·화면은 수시로 바뀝니다. 이용 전에 공식 안내를 확인하세요.")
    if TOOLS:
        cols = st.columns(NUM_COLS, gap="medium")
        for col, items in zip(cols, split_columns(TOOLS)):
            with col:
                for t in items:
                    with st.container(border=True):
                        st.markdown(f"**{t['name']}**")
                        st.markdown(t["use"])
                        st.caption(f"쓰는 단계: {t['phase']} · 이용: {t['access']}")
                        st.markdown(f'<div class="meta-line">주의 · {esc(t["caution"])}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 하단: 안내 문구·출처
# ------------------------------------------------------------
st.divider()
st.caption("이 도구의 안내는 일반 정보이며 법률·세무·통관 자문이 아닙니다. 관세·인증·계약 등 중요한 사항은 전문가 확인을 거쳐 진행하세요.")
contact_bits = [x for x in (COMPANY.get("phone"), COMPANY.get("email")) if x]
if contact_bits:
    st.caption("문의: " + " · ".join(contact_bits))
for src in SOURCE_DOCUMENTS:
    st.caption(f"참고: {src}")
