from io import BytesIO
import html
import os
import openai
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib import colors
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="nexuscouter | AI 어드바이저",
    page_icon="🌐",
    layout="wide",
)

# Streamlit Secrets에서 설정값 안전하게 불러오기
try:
    API_BASE_URL = st.secrets["API_BASE_URL"]
    API_KEY = st.secrets["API_KEY"]
    MODEL_NAME = st.secrets.get("MODEL_NAME", "gpt-6-luna")
except Exception:
    API_BASE_URL = ""
    API_KEY = ""
    MODEL_NAME = "gpt-6-luna"


# 제목과 본문의 폰트(Bold / Medium)를 분리하여 마크다운 위계를 살린 PDF 생성 함수
def create_pdf_document(title: str, content: str) -> bytes:
    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    story = []

    styles = getSampleStyleSheet()

    # 코펍체(Medium, Bold) 폰트 안전 등록
    body_font = "Helvetica"
    bold_font = "Helvetica-Bold"

    try:
        # 본문용 (Medium)
        if os.path.exists("KoPubWorld Dotum Medium.ttf"):
            pdfmetrics.registerFont(TTFont("KoPubMedium", "KoPubWorld Dotum Medium.ttf"))
            body_font = "KoPubMedium"
        elif os.path.exists("kopub.ttf"):
            pdfmetrics.registerFont(TTFont("KoPubMedium", "kopub.ttf"))
            body_font = "KoPubMedium"

        # 제목용 (Bold)
        if os.path.exists("KoPubWorld Dotum Bold.ttf"):
            pdfmetrics.registerFont(TTFont("KoPubBold", "KoPubWorld Dotum Bold.ttf"))
            bold_font = "KoPubBold"
        else:
            bold_font = body_font
    except Exception:
        pass

    # 스타일 정의 (제목과 본문의 폰트 및 크기 차별화)
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName=bold_font,
        fontSize=18,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        'ReportH2',
        parent=styles['Heading2'],
        fontName=bold_font,
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName=body_font,
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )

    # 문서 제목 추가
    safe_title = html.escape(title)
    story.append(Paragraph(safe_title, title_style))
    story.append(Spacer(1, 10))

    # 본문 마크다운 파싱 및 위계별 스타일 적용
    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 6))
            continue

        if stripped.startswith("### ") or stripped.startswith("## ") or stripped.startswith("# "):
            header_text = stripped.lstrip("#").strip()
            safe_text = html.escape(header_text)
            story.append(Paragraph(f"<b>{safe_text}</b>", h2_style))
        elif stripped.startswith("|"):
            if "---" in stripped:
                continue
            cols = [col.strip() for col in stripped.split("|") if col.strip()]
            if cols:
                row_text = " | ".join(cols)
                safe_row = html.escape(row_text)
                story.append(Paragraph(f"• {safe_row}", body_style))
        else:
            cleaned = stripped.replace("**", "")
            safe_text = html.escape(cleaned)
            story.append(Paragraph(safe_text, body_style))

    doc.build(story)
    return output.getvalue()


# 상단 탭 메뉴 구성
tab1, tab2 = st.tabs(
    ["🎯 바이어 타겟팅 & 전략 분석", "✉️ 맞춤형 영문 콜드메일 생성"]
)

# 1. 바이어 타겟팅 & 전략 분석 탭
with tab1:
    st.markdown("### 🎯 해외 바이어 페르소나 및 시장 분석")
    st.write(
        "해외 진출을 위한 타겟 시장과 바이어 조건을 설정하여 맞춤형 전략을 확인하세요."
    )

    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input(
            "수출 제품명 (또는 카테고리)",
            placeholder="예: 프리미엄 기능성 화장품 / 제약 원료",
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
            placeholder="예: 인도, 베트남, 독일 등",
            key="t1_country",
        )
        product_strength = st.text_input(
            "제품 차별점 / 강점",
            placeholder="예: 칼라테라피, 미백, 주름개선, 식물성 추출원료",
            key="t1_strength",
        )

    st.write("")
    if st.button("🚀 바이어 발굴 전략 분석 실행", key="btn_strategy"):
        if product_name and target_country:
            if not API_KEY or not API_BASE_URL:
                st.error(
                    "⚠️ Streamlit Secrets에 API 설정(API_BASE_URL, API_KEY)이 누락되었습니다."
                )
            else:
                st.info(f"[{target_country}] 진출 전략을 실시간 생성 중입니다...")
                try:
                    client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

                    prompt = (
                        f"수출 제품: {product_name} / 타겟 국가: {target_country} / "
                        f"바이어 유형: {target_type} / 강점: {product_strength}\n위 조건을 "
                        "바탕으로 핵심 바이어 타겟팅 및 수출 진출 전략을 마크다운 형식으로 작성해 주세요."
                    )

                    stream = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[{"role": "user", "content": prompt}],
                        stream=True,
                    )

                    st.markdown("---")

                    full_response = ""
                    placeholder = st.empty()

                    for chunk in stream:
                        if (
                            chunk.choices
                            and chunk.choices[0].delta
                            and chunk.choices[0].delta.content
                        ):
                            content_chunk = chunk.choices[0].delta.content
                            full_response += content_chunk
                            placeholder.markdown(full_response)

                    st.session_state["strategy_result"] = full_response

                except Exception as e:
                    st.error(f"API 호출 중 오류가 발생했습니다: {e}")
        else:
            st.warning("수출 제품명과 타겟 국가를 입력해 주세요.")

    # PDF 다운로드 버튼
    if "strategy_result" in st.session_state and st.session_state["strategy_result"]:
        pdf_data = create_pdf_document(
            f"[{target_country}] 해외 바이어 발굴 및 진출 전략 보고서",
            st.session_state["strategy_result"],
        )
        st.download_button(
            label="📥 해외 진출 전략 보고서 PDF 다운로드 (.pdf)",
            data=pdf_data,
            file_name=f"export_strategy_{target_country or 'report'}.pdf",
            mime="application/pdf",
            key="download_strategy_pdf",
        )

# 2. 맞춤형 영문 콜드메일 생성 탭
with tab2:
    st.markdown("### ✉️ 바이오 맞춤형 영문 콜드메일(Cold Mail) 자동 생성")
    st.write(
        "발견한 바이어에게 보낼 매력적인 첫인상 영문 메일 초안을 자동으로 작성합니다."
    )

    # 이전 탭의 전략 분석 결과가 있다면 안내 문구 표시
    if "strategy_result" in st.session_state and st.session_state["strategy_result"]:
        st.success("💡 첫 번째 탭에서 생성된 **진출 전략 분석 보고서 내용이 콜드메일 생성에 자동으로 연동**됩니다!")

    col3, col4 = st.columns(2)

    with col3:
        company_name = st.text_input(
            "우리회사 명칭", placeholder="예: KJ H&B", key="t2_company"
        )
        buyer_name = st.text_input(
            "바이어 회사명",
            placeholder="예: Apex Pharma India",
            key="t2_buyer",
        )

    with col4:
        item_content = st.text_input(
            "제안 품목 핵심 내용",
            placeholder="예: 기능성 화장품 및 식물성 추출원료",
            key="t2_item",
        )
        tone_manner = st.selectbox(
            "톤앤매너",
            [
                "전문적이고 격식 있는 (Formal)",
                "친근하고 설득력 있는 (Friendly & Persuasive)",
                "간결하고 명확한 (Concise & Direct)",
            ],
            key="t2_tone",
        )

    st.write("")
    if st.button("✨ 영문 제안 메일 생성하기", key="btn_mail"):
        if company_name and buyer_name and item_content:
            if not API_KEY or not API_BASE_URL:
                st.error(
                    "⚠️ Streamlit Secrets에 API 설정(API_BASE_URL, API_KEY)이 누락되었습니다."
                )
            else:
                st.info("이전 분석 보고서 내용을 참고하여 맞춤형 영문 콜드메일 초안을 작성 중입니다...")
                try:
                    client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
                    
                    # 첫 번째 탭의 분석 결과 가져오기 (연동)
                    strategy_context = st.session_state.get("strategy_result", "별도 분석 내용 없음")

                    mail_prompt = (
                        f"보내는 회사: {company_name} / 수신 바이어: {buyer_name} / 제안 품목: {item_content} / 톤앤매너: {tone_manner}\n\n"
                        f"[참고할 이전 시장 분석 및 진출 전략 보고서 핵심 내용]:\n{strategy_context[:1200]}\n\n"
                        "위의 시장 분석 내용과 전략적 소구점을 적극적으로 반영하여, 바이어의 마음을 사로잡을 수 있는 맞춤형 영문 콜드메일 초안(Subject 및 본문)을 작성해 주세요."
                    )

                    stream = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[{"role": "user", "content": mail_prompt}],
                        stream=True,
                    )

                    st.markdown("---")

                    full_mail = ""
                    mail_placeholder = st.empty()

                    for chunk in stream:
                        if (
                            chunk.choices
                            and chunk.choices[0].delta
                            and chunk.choices[0].delta.content
                        ):
                            content_chunk = chunk.choices[0].delta.content
                            full_mail += content_chunk
                            mail_placeholder.markdown(full_mail)

                    st.session_state["mail_result"] = full_mail

                except Exception as e:
                    st.error(f"API 호출 중 오류가 발생했습니다: {e}")
        else:
            st.warning("필수 입력 항목을 모두 작성해 주세요.")

    # PDF 다운로드 버튼
    if "mail_result" in st.session_state and st.session_state["mail_result"]:
        pdf_mail_data = create_pdf_document(
            f"[{buyer_name}] 영문 콜드메일 제안서",
            st.session_state["mail_result"],
        )
        st.download_button(
            label="📥 영문 콜드메일 초안 PDF 다운로드 (.pdf)",
            data=pdf_mail_data,
            file_name=f"cold_mail_{buyer_name or 'buyer'}.pdf",
            mime="application/pdf",
            key="download_mail_pdf",
        )
