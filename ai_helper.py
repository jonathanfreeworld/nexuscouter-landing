"""AI 도우미 보조 모듈: 질문 조립과 (선택) Anthropic API 호출.

- API 키가 없으면 is_enabled()가 False이고, 앱은 '질문 복사' 방식으로만 동작한다.
- 키는 Streamlit secrets 또는 환경변수에서만 읽는다. 코드에 직접 적지 않는다.
"""
import os

DEFAULT_MODEL = "claude-sonnet-5-5"   # secrets/환경변수 ANTHROPIC_MODEL 로 변경 가능
MAX_INPUT_CHARS = 8000
MAX_OUTPUT_TOKENS = 1800

SYSTEM_PROMPT = (
    "당신은 K-푸드·K-뷰티 수출 담당자의 실무를 돕는 업무 도우미입니다. "
    "사용자가 제공한 정보만 근거로 초안과 정리를 만듭니다. "
    "관세율·인증 요건·법규·계약 해석은 확정적으로 단정하지 말고 '확인 필요'와 공식 확인처를 안내하세요. "
    "제공되지 않은 가격·수량·인증·실적은 만들지 말고 [입력 필요]로 남기세요. "
    "최신 정보를 직접 조회할 수 없으면 그렇게 밝히세요. "
    "한국어로 답하되, 요청된 외국어 문안은 그 언어로 작성하세요."
)


def _setting(name, default=None):
    """Streamlit secrets → 환경변수 순으로 설정값을 찾는다."""
    try:
        import streamlit as st
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass
    return os.environ.get(name, default)


def build_prompt(task: dict, values: dict, common_rules: str = "") -> str:
    """입력값을 질문 틀에 채운다. 빈 칸은 [입력 필요]로 남긴다."""
    text = task["prompt"]
    for field in task["fields"]:
        key = field["key"]
        value = (values.get(key) or "").strip() or "[입력 필요]"
        text = text.replace("{" + key + "}", value)
    if common_rules:
        text = f"{text}\n\n{common_rules}"
    return text


def is_enabled() -> bool:
    if not _setting("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def max_calls_per_session() -> int:
    try:
        return int(_setting("AI_CALLS_PER_SESSION", "8"))
    except ValueError:
        return 8


def ask_ai(prompt: str, client=None) -> str:
    """질문을 보내 답변 텍스트를 돌려준다. client는 테스트용 주입."""
    if len(prompt) > MAX_INPUT_CHARS:
        raise ValueError(f"입력이 너무 깁니다. {MAX_INPUT_CHARS:,}자 이내로 줄여 주세요.")
    if client is None:
        import anthropic
        client = anthropic.Anthropic(api_key=_setting("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=_setting("ANTHROPIC_MODEL", DEFAULT_MODEL),
        max_tokens=MAX_OUTPUT_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = [b.text for b in response.content if getattr(b, "type", "") == "text"]
    return "".join(parts).strip()
