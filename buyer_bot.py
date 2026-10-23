
import time
import logging

import streamlit as st
from openai import OpenAI, APIError, APITimeoutError, RateLimitError


# ==================================================
# 1. 기본 설정
# ==================================================
st.set_page_config(
    page_title="nexuscouter | AI 어드바이저",
    page_icon="🌐",
    layout="wide",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexuscouter")

DEFAULT_MODEL = "gpt-6-luna"
DEFAULT_MAX_TOKENS = 4000
MAX_RETRIES = 3
MAX_CONTINUATIONS = 3


# ==================================================
# 2. API 설정
# ==================================================
def load_config():
    try:
        base_url = str(st.secrets["API_BASE_URL"]).strip()
        api_key = str(st.secrets["API_KEY"]).strip()
        model = str(
            st.secrets.get("MODEL_NAME", DEFAULT_MODEL)
        ).strip()

        token_parameter = str(
            st.secrets.get(
                "TOKEN_PARAMETER", "max_completion_tokens"
            )
        ).strip()

        max_tokens = int(
            st.secrets.get(
                "MAX_COMPLETION_TOKENS", DEFAULT_MAX_TOKENS
            )
        )

        timeout = float(
            st.secrets.get("API_TIMEOUT", 90)
        )

        if not base_url or not api_key or not model:
            raise ValueError("필수 API 설정값이 비어 있습니다.")

        if token_parameter not in (
            "max_completion_tokens",
            "max_tokens",
        ):
            raise ValueError("TOKEN_PARAMETER 설정을 확인하세요.")

        if not 256 <= max_tokens <= 32000:
            raise ValueError(
                "MAX_COMPLETION_TOKENS는 256~32000이어야 합니다."
            )

        if not 10 <= timeout <= 300:
            raise ValueError("API_TIMEOUT은 10~300이어야 합니다.")

        return {
            "base_url": base_url,
            "api_key": api_key,
            "model": model,
            "token_parameter": token_parameter,
            "max_tokens": max_tokens,
            "timeout": timeout,
        }, None

    except Exception as exc:
        logger.warning(
            "API 설정 로드 실패: %s", type(exc).__name__
        )
        return None, (
            "API 설정을 읽을 수 없습니다. "
            ".streamlit/secrets.toml 파일을 확인하세요."
        )


CONFIG, CONFIG_ERROR = load_config()


# ==================================================
# 3. API 클라이언트
# ==================================================
@st.cache_resource
def get_client(base_url, api_key, timeout):
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=timeout,
        max_retries=0,
    )


# ==================================================
# 4. API 요청 및 재시도
# ==================================================
def request_completion(client, messages):
    kwargs = {
        "model": CONFIG["model"],
        "messages": messages,
        CONFIG["token_parameter"]: CONFIG["max_tokens"],
    }

    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            return client.chat.completions.create(**kwargs)

        except (APITimeoutError, RateLimitError, APIError) as exc:
            last_error = exc
            status = getattr(exc, "status_code", None)

            # 인증 오류, 잘못된 요청 등은 반복하지 않습니다.
            if (
                status is not None
                and status not in (408, 409, 429)
                and status < 500
            ):
                raise

            if attempt < MAX_RETRIES - 1:
                time.sleep(min(2 ** attempt, 4))

        except Exception:
            raise

    raise RuntimeError(
        "API 요청이 반복해서 실패했습니다."
    ) from last_error


# ==================================================
# 5. 통합 텍스트 생성 함수
# ==================================================
def generate_text(prompt, progress=None):
    if CONFIG is None:
        raise RuntimeError(CONFIG_ERROR)

    client = get_client(
        CONFIG["base_url"],
        CONFIG["api_key"],
        CONFIG["timeout"],
    )

    messages = [
        {
            "role": "system",
            "content": (
                "당신은 전문적인 글로벌 수출 전략 및 B2B 영업 전문가입니다. "
                "요청에 맞는 구체적이고 실용적인 결과를 작성하세요. "
                "확인하지 않은 시장 통계, 인증, 회사 정보는 만들어내지 마세요. "
                "요청한 결과물을 완결된 형태로 제공하세요."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    result_parts = []

    for step in range(MAX_CONTINUATIONS + 1):
        if progress:
            progress.update(
                label=(
                    "AI 응답 생성 중..."
                    if step == 0
                    else f"중단된 응답 이어쓰기 중 ({step}/{MAX_CONTINUATIONS})..."
                ),
                state="running",
            )

        response = request_completion(client, messages)

        if not response.choices:
            raise RuntimeError("API 응답에 choices가 없습니다.")

        choice = response.choices[0]
        content = choice.message.content or ""
        finish_reason = choice.finish_reason

        if content.strip():
            result_parts.append(content.strip())

        # 정상 종료
        if finish_reason == "stop":
            result = "\n\n".join(result_parts).strip()

            if not result:
                raise RuntimeError(
                    "모델이 빈 결과를 반환했습니다."
                )

            return result

        # 토큰 한도로 응답이 잘린 경우
        if finish_reason == "length":
            # 일부 결과가 있으면 세션에 임시 저장해 복구합니다.
            partial = "\n\n".join(result_parts).strip()
            if partial:
                st.session_state["working_result"] = partial

            if step >= MAX_CONTINUATIONS:
                raise RuntimeError(
                    "응답이 토큰 한도에 반복해서 도달했습니다. "
                    "현재까지 생성된 결과는 임시 보관되었습니다. "
                    "MAX_COMPLETION_TOKENS를 늘리거나 요청을 나누세요."
                )

            messages.append({
                "role": "assistant",
                "content": content,
            })
            messages.append({
                "role": "user",
                "content": (
                    "이전 응답의 마지막 부분부터 자연스럽게 이어서 작성하세요. "
                    "이미 작성한 내용을 반복하지 말고 누락된 부분과 결론을 "
                    "완성하세요."
                ),
            })
            continue

        if finish_reason == "content_filter":
            raise RuntimeError(
                "콘텐츠 필터로 응답이 제한되었습니다."
            )

        raise RuntimeError(
            f"응답이 정상적으로 완료되지 않았습니다: {finish_reason}"
        )

    raise RuntimeError("최대 생성 횟수를 초과했습니다.")


# ==================================================
# 6. 결과 생성 실행 및 보존
# ==================================================
def run_generation(prompt, result_key, task_name):
    st.session_state["working_result"] = ""

    status = st.status(
        f"{task_name} 시작...",
        expanded=True,
    )

    try:
        result = generate_text(prompt, status)

        # 완성된 결과 저장
        st.session_state[result_key] = result
        st.session_state["working_result"] = ""

        status.update(
            label=f"{task_name} 완료",
            state="complete",
            expanded=False,
        )
        st.success("결과가 생성되었습니다.")

    except Exception as exc:
        logger.exception("%s 실패", task_name)

        # 중간 생성물이 있으면 임시 결과로 보존합니다.
        partial = st.session_state.get("working_result", "")
        if partial:
            st.session_state[result_key] = partial

        status.update(
            label=f"{task_name} 실패",
            state="error",
            expanded=True,
        )

        st.error(
            "요청을 완료하지 못했습니다. API 설정, 모델 지원 여부, "
            "네트워크 상태를 확인해 주세요."
        )
        st.caption(f"오류 유형: {type(exc).__name__}")

        if partial:
            st.warning(
                "완성되지 않은 중간 결과를 표시합니다. "
                "최종 결과로 사용하기 전에 확인해 주세요."
            )


def show_result(result_key, filename, title):
    result = st.session_state.get(result_key, "")

    if result:
        st.markdown("---")
        st.subheader(title)
        st.markdown(result)

        st.download_button(
            "📥 결과 다운로드 (.md)",
            data=result,
            file_name=filename,
            mime="text/markdown",
            key=f"download_{result_key}",
        )


# ==================================================
# 7. 세션 상태 초기화
# ==================================================
for key in ("strategy_result", "mail_result", "working_result"):
    if key not in st.session_state:
        st.session_state[key] = ""


# ==================================================
# 8. 페이지 헤더
# ==================================================
st.title("🌐 nexuscouter | AI 어드바이저")
st.caption(
    "글로벌 바이어 발굴 전략 분석 및 영문 콜드메일 생성"
)

if CONFIG is None:
    st.error(CONFIG_ERROR)
    st.stop()


# ==================================================
# 9. 탭 생성
# ==================================================
tab1, tab2 = st.tabs([
    "🎯 바이어 타겟팅 & 전략 분석",
    "✉️ 맞춤형 영문 콜드메일 생성",
])


# ==================================================
# 10. 바이어 전략 분석
# ==================================================
with tab1:
    st.header("🎯 해외 바이어 페르소나 및 시장 분석")
    st.write(
        "목표 국가와 제품 특성에 맞는 바이어 발굴 전략을 분석합니다."
    )

    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input(
            "수출 제품명 또는 카테고리",
            placeholder="예: 프리미엄 기능성 화장품",
            key="t1_product",
        )

        target_type = st.selectbox(
            "타겟 바이어 유형",
            [
                "현지 총판 디스트리뷰터 (Distributor)",
                "수입사 / 도매상 (Importer / Wholesaler)",
                "현지 온·오프라인 리테일러",
                "기타 파트너",
            ],
            key="t1_type",
        )

    with col2:
        target_country = st.text_input(
            "타겟 국가",
            placeholder="예: 인도, 베트남, 독일",
            key="t1_country",
        )

        product_strength = st.text_area(
            "제품 차별점 및 강점",
            placeholder="예: 식물성 원료, 특허 기술, 가격 경쟁력",
            key="t1_strength",
        )

    if st.button(
        "🚀 바이어 발굴 전략 분석 실행",
        type="primary",
        key="btn_strategy",
    ):
        if not product_name.strip() or not target_country.strip():
            st.warning("제품명과 타겟 국가를 입력해 주세요.")
        else:
            prompt = f"""
다음 정보를 바탕으로 해외 수출 전략 보고서를 한국어로 작성하세요.

[입력 정보]
- 수출 제품: {product_name.strip()}
- 타겟 국가: {target_country.strip()}
- 바이어 유형: {target_type}
- 제품 강점: {product_strength.strip() or "미입력"}

[필수 보고서 항목]
1. 시장 진출 기회 및 주요 고려 사항
2. 이상적인 바이어 페르소나
3. 우선 공략할 바이어 유형과 선정 이유
4. 바이어 발굴 채널 및 검색 키워드
5. 바이어에게 제안할 핵심 가치
6. 경쟁 제품 대비 차별화 전략
7. 첫 접촉 및 후속 영업 전략
8. 30일 실행 계획
9. 국가별 인증, 수입 규제 및 확인 방법

표와 체크리스트를 적절히 활용하세요.
확인되지 않은 통계와 회사명을 사실처럼 작성하지 마세요.
규제 정보는 공식 기관에서 확인하도록 안내하세요.
완성된 보고서와 실행 계획까지 작성하세요.
"""

            run_generation(
                prompt,
                "strategy_result",
                "바이어 전략 분석",
            )

    show_result(
        "strategy_result",
        "buyer_strategy.md",
        "📊 바이어 타겟팅 전략 분석 결과",
    )


# ==================================================
# 11. 영문 콜드메일
# ==================================================
with tab2:
    st.header("✉️ 맞춤형 영문 콜드메일 생성")
    st.write(
        "해외 바이어에게 보낼 영문 B2B 제안 메일을 작성합니다."
    )

    col3, col4 = st.columns(2)

    with col3:
        company_name = st.text_input(
            "우리 회사명",
            placeholder="예: KJ H&B",
            key="t2_company",
        )

        buyer_name = st.text_input(
            "바이어 회사명",
            placeholder="예: Apex Pharma India",
            key="t2_buyer",
        )

    with col4:
        item_content = st.text_area(
            "제안 품목 및 핵심 내용",
            placeholder="제품 특징, 인증, 주요 장점을 입력하세요.",
            key="t2_item",
        )

        tone_manner = st.selectbox(
            "메일 톤앤매너",
            [
                "전문적이고 격식 있는 (Formal)",
                "친근하고 설득력 있는 (Friendly & Persuasive)",
                "간결하고 명확한 (Concise & Direct)",
            ],
            key="t2_tone",
        )

    if st.button(
        "✨ 영문 제안 메일 생성하기",
        type="primary",
        key="btn_mail",
    ):
        if not all([
            company_name.strip(),
            buyer_name.strip(),
            item_content.strip(),
        ]):
            st.warning(
                "우리 회사명, 바이어 회사명, 제안 품목을 입력해 주세요."
            )
        else:
            prompt = f"""
Write a complete B2B cold email in English.

[Sender company]
{company_name.strip()}

[Recipient company]
{buyer_name.strip()}

[Product or proposal]
{item_content.strip()}

[Preferred tone]
{tone_manner}

[Required output]
1. Two alternative subject lines
2. A professional greeting
3. A concise introduction of the sender
4. The product's relevant business value
5. A clear and polite call to action
6. A professional closing

Do not invent certifications, customer references, test results, or achievements.
Do not claim to have researched the recipient without supplied evidence.
Use natural business English and avoid exaggerated marketing claims.
Return the complete email draft, not writing advice.
"""

            run_generation(
                prompt,
                "mail_result",
                "영문 콜드메일 생성",
            )

    show_result(
        "mail_result",
        "cold_email.md",
        "📨 생성된 영문 콜드메일",
    )


# ==================================================
# 12. 안내
# ==================================================
st.markdown("---")
st.caption(
    "AI 생성 결과는 실제 계약, 시장 진입 및 수출 진행 전에 "
    "공식 자료를 통해 확인하세요."
)
