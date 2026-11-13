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
    "콘텐츠 검색",
    placeholder="예: 할랄, FDA, MoCRA, FOB, 바이어, 콜드체인, RAG",
)

def chapter_search_text(chapter):
    """챕터의 주요 텍스트 필드를 합쳐 검색 대상으로 사용한다."""
    fields = [
        "title",
        "summary",
        "learning_goal",
        "body",
    ]
    values = [str(chapter.get(key, "")) for key in fields]

    for key in ("points", "steps", "checklist", "deliverables"):
        value = chapter.get(key, [])
        if isinstance(value, (list, tuple)):
            values.extend(str(v) for v in value)
        elif value:
            values.append(str(value))

    return " ".join(values).casefold()


filtered_chapters = []

for chapter in CHAPTERS:
    chapter_category = CATEGORIES.get(chapter.get("cat"), "기타")

    if selected_category != "전체" and chapter_category != selected_category:
        continue

    if search_query.strip():
        if search_query.strip().casefold() not in chapter_search_text(chapter):
            continue

    filtered_chapters.append(chapter)

# 장 번호 순으로 정렬
filtered_chapters.sort(key=lambda item: int(item.get("no", 0)))

st.caption(
    f"검색 결과: {len(filtered_chapters)}개 콘텐츠 / 전체 {len(CHAPTERS)}개"
)

# ------------------------------------------------------------
# 카드형 상세 콘텐츠
# ------------------------------------------------------------
if not filtered_chapters:
    st.warning("검색 조건에 해당하는 콘텐츠가 없다. 검색어 또는 카테고리를 변경한다.")
else:
    columns = st.columns(3)

    for idx, chapter in enumerate(filtered_chapters):
        with columns[idx % 3]:
            chapter_no = chapter.get("no", idx + 1)
            title = chapter.get("title", "제목 없음")
            summary = chapter.get("summary", "")

            with st.expander(f"제{chapter_no}장. {title}", expanded=False):
                if summary:
                    st.markdown(f"**핵심 내용**")
                    st.write(summary)

                if chapter.get("learning_goal"):
                    st.markdown("**학습 목표**")
                    st.write(chapter["learning_goal"])

                if chapter.get("body"):
                    st.markdown("**실무 관점**")
                    st.write(chapter["body"])

                steps = chapter.get("steps", [])
                if steps:
                    st.markdown("**실행 절차**")
                    for step in steps:
                        st.markdown(f"- {step}")

                points = chapter.get("points", [])
                if points:
                    st.markdown("**핵심 실무 포인트**")
                    for point in points:
                        st.markdown(f"- {point}")

                checklist = chapter.get("checklist", [])
                if checklist:
                    st.markdown("**점검 체크리스트**")
                    for item in checklist:
                        st.markdown(f"- [ ] {item}")

                deliverables = chapter.get("deliverables", [])
                if deliverables:
                    st.markdown("**실습 산출물**")
                    for item in deliverables:
                        st.markdown(f"- {item}")

                st.caption(
                    "교육용 실무 가이드이다. 실제 계약·통관·인증 판단은 "
                    "제품 및 목적국의 최신 공식 기준과 전문가 검토를 거쳐야 한다."
                )

# ------------------------------------------------------------
# 하단 안내
# ------------------------------------------------------------
st.divider()
st.caption(
    "본 콘텐츠는 교육 및 업무 검토를 위한 참고자료이며, "
    "법률·세무·관세·제품안전 관련 최종 판단을 대체하지 않는다."
)
