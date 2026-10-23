import streamlit as st
import pdfplumber
import pandas as pd
import re
import tempfile
import os

st.set_page_config(
    page_title="EU 화장품 규정 컴플라이언스 검수 툴",
    page_icon="🛡️",
    layout="wide"
)

st.title("🇪🇺 유럽 화장품 규정(EC) No 1223/2009 검수 툴")
st.markdown("새로운 제품의 INCI 성분표 PDF 파일을 업로드하면 유럽 규정(Annex II/III)과 즉시 대조하여 검수 리포트를 생성합니다.")

# 기본 샘플 파일명 (경로에 있을 경우 기본 제공용)
DEFAULT_PRODUCT_PDF = "UV PROTECTOR ESSENCE_INCI.pdf"

@st.cache_data
def load_regulations():
    """규제 대상 성분 베이스 (필수 안전망 및 샘플 데이터)"""
    banned_substances = {
        "benzene", "chloroform", "methanol", "formaldehyde", "dioxane", 
        "lead acetate", "mercury", "bithionol", "vinyl chloride", "zirconium"
    }
    restricted_substances = {
        "salicylic acid": "최대 허용 농도 2% (사용 조건 확인 필요)",
        "retinol": "바디/페이스 제품 최대 허용 농도 기준 준수",
        "phenoxyethanol": "최대 허용 농도 1% 제한"
    }
    return banned_substances, restricted_substances

def extract_text_from_pdf_stream(pdf_file_path):
    """업로드된 임시 PDF 파일에서 텍스트 추출"""
    text = ""
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        st.error(f"PDF 파일을 읽는 중 오류가 발생했습니다: {e}")
    return text

def parse_product_ingredients(pdf_file_path):
    """INCI PDF에서 전성분 파싱"""
    raw_text = extract_text_from_pdf_stream(pdf_file_path)
    cleaned_items = []
    lines = raw_text.split('\n')
    for line in lines:
        tokens = [item.strip() for item in line.replace(';', ',').split(',') if item.strip()]
        for token in tokens:
            token_clean = re.sub(r'^\d+[\.\)]\s*', '', token)
            if len(token_clean) > 1:
                cleaned_items.append(token_clean)
    return list(set(cleaned_items))

# --- 사이드바: 파일 업로드 및 설정 ---
st.sidebar.header("📁 제품 INCI 파일 업로드")
uploaded_file = st.sidebar.file_uploader("새로운 INCI 성분표 PDF 파일을 업로드하세요", type=["pdf"])

target_path = None

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        target_path = tmp_file.name
    st.sidebar.success(f"✅ 업로드 완료: {uploaded_file.name}")
else:
    if os.path.exists(DEFAULT_PRODUCT_PDF):
        st.sidebar.info(f"💡 업로드된 파일이 없어 기본 샘플 파일(`{DEFAULT_PRODUCT_PDF}`)로 검수를 진행합니다.")
        target_path = DEFAULT_PRODUCT_PDF
    else:
        st.sidebar.warning("⚠️ 검수할 INCI PDF 파일을 업로드해 주세요.")

# --- 검수 실행 버튼 ---
if st.sidebar.button("🚀 규정 검수 실행", type="primary"):
    if not target_path or not os.path.exists(target_path):
        st.error("❌ 분석할 유효한 PDF 파일이 없습니다. 파일을 업로드해 주세요.")
    else:
        with st.spinner("전성분을 분석하고 유럽 규정과 대조하는 중입니다..."):
            ingredients = parse_product_ingredients(target_path)
            
            if not ingredients:
                st.warning("⚠️ PDF 파일에서 전성분 텍스트를 추출하지 못했습니다. 텍스트 레이어 형태의 PDF인지 확인해 주세요.")
            else:
                banned_set, restricted_dict = load_regulations()
                
                results = []
                for ing in ingredients:
                    ing_lower = ing.lower()
                    status = "🟢 Safe (안전)"
                    remark = "규제 대상 아님 (정상)"
                    
                    if any(b in ing_lower for b in banned_set):
                        status = "🔴 PROHIBITED (사용 금지 - Annex II)"
                        remark = "유럽 규정상 전면 금지된 성분입니다."
                    elif any(r in ing_lower for r in restricted_dict.keys()):
                        for r, cond in restricted_dict.items():
                            if r in ing_lower:
                                status = "🟡 RESTRICTED (사용 제한 - Annex III)"
                                remark = cond
                                break
                                
                    results.append({
                        "Input INCI": ing,
                        "Compliance Status": status,
                        "Remark": remark
                    })
                    
                df_result = pd.DataFrame(results)
                
                st.success(f"✅ 검수 완료! 총 {len(ingredients)}개의 성분이 분석되었습니다.")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("전체 분석 성분 수", f"{len(ingredients)}개")
                col2.metric("금지 성분(Annex II)", f"{len(df_result[df_result['Compliance Status'].str.contains('PROHIBITED')])}건")
                col3.metric("제한 성분(Annex III)", f"{len(df_result[df_result['Compliance Status'].str.contains('RESTRICTED')])}건")
                
                st.markdown("---")
                st.subheader("📋 상세 검수 리포트")
                st.dataframe(df_result, use_container_width=True)
                
                csv_data = df_result.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label="📥 검수 결과 CSV 다운로드",
                    data=csv_data,
                    file_name="cpnp_compliance_report.csv",
                    mime="text/csv"
                )
else:
    st.info("👈 왼쪽 사이드바에서 새로운 **INCI PDF 파일을 업로드**한 뒤, **[규정 검수 실행]** 버튼을 눌러보세요.")