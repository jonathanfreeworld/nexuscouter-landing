from io import BytesIO
import openai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import streamlit as st
import os

# (중략 - 기존 상단 설정 및 API 키 로드 부분 유지)

def create_pdf_document(title: str, content: str) -> bytes:
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []

    styles = getSampleStyleSheet()
    
    # 서버 환경에 맞는 한글 폰트 적용 시도
    font_registered = False
    try:
        linux_font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
        if os.path.exists(linux_font_path):
            pdfmetrics.registerFont(TTFont('Malgun', linux_font_path))
            font_registered = True
    except Exception:
        pass

    font_name = 'Malgun' if font_registered else 'Helvetica'

    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=16,
        leading=22,
        textColor='#1E3A8A',
        spaceAfter=15
    )

    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=15,
        textColor='#333333',
        spaceAfter=8
    )

    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 10))

    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 8))
            continue
        clean_line = stripped.replace("**", "")
        story.append(Paragraph(clean_line, body_style))

    doc.build(story)
    return output.getvalue()
