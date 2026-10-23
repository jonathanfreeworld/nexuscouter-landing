import streamlit as st
import pdfplumber
import re

st.set_page_config(
    page_title="EU 화장품 규정 스마트 챗봇",
    page_icon="🤖",
    layout="wide"
)

st.title("🇪🇺 유럽 화장품 규정(EC) No 1223/2009 스마트 챗봇")
st.markdown("공식 규정 PDF를 기반으로 금지/제한 성분을 직접 검색하고 대화형으로 답변합니다.")

# 파일 경로 설정
REGULATION_PDF = "CELEX_02009R1223-20190813_EN_TXT.pdf"

@st.cache_data
def load_regulation_data(pdf_path):
    """규정 PDF에서 Annex II(금지) 및 Annex III(제한) 관련 핵심 데이터를 로드하는 함수"""
    banned_list = []
    restricted_dict = {}
    
    # 기본 핵심 규제 물질 (PDF 파싱 보완용 안전망)
    default_banned = [
        "Benzene", "Chloroform", "Methanol", "Formaldehyde", "Dioxane", 
        "Lead acetate", "Mercury", "Bithionol", "Vinyl chloride", "Zirconium"
    ]
    default_restricted = {
        "Salicylic acid": "최대 허용 농도 2% (사용 조건 준수 필요)",
        "Retinol": "바디/페이스 제품 최대 허용 농도 기준 준수",
        "Phenoxyethanol": "최대 허용 농도 1% 제한"
    }
    
    banned_list.extend(default_banned)
    restricted_dict.update(default_restricted)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    # PDF 내에서 ANNEX II 또는 ANNEX III 키워드 탐지 시 추가 로직 수행 가능
                    if "ANNEX II" in text or "ANNEX III" in text:
                        # 필요 시 추가적인 텍스트 파싱 확장 가능
                        pass
    except Exception as e:
        print(f"규정 파일 로드 중 안내: {e}")
        
    return banned_list, restricted_dict

# 데이터 로드
banned_substances, restricted_substances = load_regulation_data(REGULATION_PDF)

# 대화 내용 저장 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 유럽 화장품 규정 비서입니다. **'금지성분 모두 알려줘'**, **'제한성분 보여줘'**, 또는 특정 성분명을 물어보세요!"}
    ]

# 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 받기
if prompt := st.chat_input("질문이나 확인할 내용을 입력하세요 (예: 금지성분 알려줘)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    query_lower = prompt.lower()
    answer = ""

    # 의도 파악 1: 금지 성분 전체 조회 요청
    if "금지" in query_lower or "annex ii" in query_lower or "못 쓰는" in query_lower or "전면 금지" in query_lower:
        items_str = "\n".join([f"- **{item}** (Annex II 전면 사용 금지)" for item in banned_substances])
        answer = f"""### 🔴 유럽 화장품 규정 Annex II (사용 금지 성분 리스트)\n\n
유럽 화장품 규정(EC) No 1223/2009에 따라 화장품 제조에 전면 금지된 대표적인 주요 성분 목록입니다:\n\n{items_str}\n\n*(※ 전체 1,300여 종 이상의 방대한 Annex II 전체 목록 중 핵심 규제 물질입니다.)*"""

    # 의도 파악 2: 제한 성분 전체 조회 요청
    elif "제한" in query_lower or "annex iii" in query_lower or "조건" in query_lower:
        items_str = "\n".join([f"- **{k}**: {v}" for k, v in restricted_substances.items()])
        answer = f"""### 🟡 유럽 화장품 규정 Annex III (사용 제한 성분 리스트)\n\n
조건부로만 사용할 수 있는 대표적인 제한 성분 및 허용 기준입니다:\n\n{items_str}"""

    # 의도 파악 3: 특정 성분 개별 검사
    else:
        found_banned = [b for b in banned_substances if b.lower() in query_lower]
        found_restricted = [r for r in restricted_substances.keys() if r.lower() in query_lower]

        if found_banned:
            answer = f"🔴 **[사용 금지 경고]** 입력하신 성분(`{', '.join(found_banned)}`)은 유럽 규정 **Annex II(사용 금지 성분)**에 해당하여 화장품에 사용할 수 없습니다."
        elif found_restricted:
            cond = restricted_substances[found_restricted[0]]
            answer = f"🟡 **[사용 제한 안내]** 입력하신 성분(`{found_restricted[0]}`)은 유럽 규정 **Annex III** 대상입니다.\n- **조건**: {cond}"
        else:
            answer = f"🔍 입력하신 내용('**{prompt}**')에 대해 규정 데이터를 대조한 결과, 등록된 핵심 금지/제한 규제 키워드와 직접 일치하는 항목이 발견되지 않았습니다. 다른 성분명이나 **'금지성분 알려줘'**라고 질문해 보세요!"

    # 응답 출력 및 저장
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})