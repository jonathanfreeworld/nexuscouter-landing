import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services import fetch_g2b_notices, fetch_bizinfo_notices, analyze_notice_with_ai

st.set_page_config(
    page_title="Nexus Couter - 공공조달 & 지원사업 AI 에이전트",
    layout="wide"
)

st.title("넥서스카우터 (Nexus Couter) 공공조달 & 지원사업 AI 에이전트")
st.markdown("나라장터(G2B) 입찰 공고와 기업마당(Bizinfo) 지원사업을 실시간으로 탐색하고, 자사 역량 기반 맞춤형 제안서를 자동 생성합니다.")

# 사이드바 설정
st.sidebar.header("검색 조건 설정")

default_start = datetime.today() - timedelta(days=30)
default_end = datetime.today()
date_range = st.sidebar.date_input(
    "조회 기간 선택",
    value=(default_start, default_end)
)

keyword = st.sidebar.text_input("검색 키워드", value="AI")
data_source = st.sidebar.selectbox("데이터 소스 선택", ["나라장터 (G2B)", "기업마당 (Bizinfo)"])
search_clicked = st.sidebar.button("공고 검색 및 AI 분석 실행")

# 검색 실행 및 세션 저장
if search_clicked:
    with st.spinner("데이터를 수집하고 조건에 맞는 공고를 필터링 중입니다..."):
        if "나라장터" in data_source:
            raw_notices = fetch_g2b_notices(keyword)
        else:
            raw_notices = fetch_bizinfo_notices(keyword)
            
        st.session_state["notices"] = raw_notices
        st.session_state["keyword"] = keyword
        st.session_state["data_source"] = data_source

# 메인 화면 출력
if "notices" in st.session_state and st.session_state["notices"]:
    current_keyword = st.session_state.get("keyword", keyword)
    current_source = st.session_state.get("data_source", data_source)
    notices = st.session_state["notices"]
    
    st.markdown("---")
    st.subheader(f"검색된 공고 목록 ({current_source})")
    st.caption(f"검색 키워드: '{current_keyword}' | 총 {len(notices)}건 발견")
    
    for idx, notice in enumerate(notices):
        title = notice.get('pblancNm', notice.get('bidNtceNm', '제목 없음'))
        org = notice.get('jrsdInsttNm', '소관기관 미상')
        notice_id = notice.get('pblancId', notice.get('bidNtceNo', 'N/A'))
        summary = notice.get('bsnsSumryCn', '상세 내용 없음')
        deadline = notice.get('reqstBeginEndDe', notice.get('bidClseDt', '마감일 정보 없음'))
        notice_url = notice.get('bidNtceDtlUrl', notice.get('pblancUrl', 'https://www.g2b.go.kr'))

        with st.expander(f"[{org}] {title} (마감: {deadline})"):
            st.write(f"**공고 번호/ID**: `{notice_id}`")
            st.write(f"**사업 개요**: {summary}")
            st.write(f"**신청/마감 기한**: {deadline}")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                st.link_button("나라장터/기업마당 원문 상세페이지 바로가기", notice_url, use_container_width=True)
            with col_btn2:
                ai_btn_clicked = st.button("AI 맞춤형 제안서 생성", key=f"btn_ai_{idx}", use_container_width=True)

            # 세션 키 정의
            report_key = f"ai_report_{idx}"

            # 버튼이 눌렸을 때 스트리밍 출력
            if ai_btn_clicked:
                st.markdown("---")
                st.markdown("### AI 수주 전략 및 제안서 리포트")
                with st.spinner("nexuscouter 맞춤형 수주 전략 리포트 작성 중..."):
                    stream_generator = analyze_notice_with_ai(notice)
                    full_response = st.write_stream(stream_generator)
                    st.session_state[report_key] = full_response

            # 이미 생성되어 세션에 있는 리포트 유지 출력
            elif report_key in st.session_state:
                st.markdown("---")
                st.markdown("### AI 수주 전략 및 제안서 리포트")
                st.markdown(st.session_state[report_key])
else:
    st.info("왼쪽 사이드바에서 조회 기간과 검색 키워드를 설정한 후 '공고 검색 및 AI 분석 실행' 버튼을 눌러주세요.")