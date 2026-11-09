from __future__ import annotations
import os
import requests
from openai import OpenAI, OpenAIError
import streamlit as st

API_BASE_URL = "https://mlapi.run/2b112090-5609-4dde-87fb-161933470bde/v1"

def get_openai_client() -> OpenAI:
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        base_url = st.secrets.get("BASE_URL", API_BASE_URL)
    except Exception:
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3OTQyMDcyNDgsIm5iZiI6MTc5NDIwNzI0OCwia2V5X2lkIjoiODczMTYyMDUtNTk3NS00YTlkLWI2Y2ItODE0NTU0Y2I3ZDNiIn0.HIZ5YGHHqLwTCwyPQQ7X75y5YB_ezgwe3AmBb5wLtVE"
        base_url = API_BASE_URL
        
    return OpenAI(api_key=api_key, base_url=base_url)

def fetch_g2b_notices(keyword: str = "AI") -> list[dict]:
    all_notices = [
        {"bidNtceNo": "20261109-G2B-01", "jrsdInsttNm": "한국지능정보사회진흥원", "bidNtceNm": f"공공부문 생성형 AI 기반 지능형 업무 자동화 및 {keyword} 솔루션 고도화 용역", "bsnsSumryCn": "행정 효율성 향상을 위한 LLM 기반 에이전트 구축, 공공데이터 파이프라인 연동 및 실시간 검증 시스템 개발", "bidClseDt": "2026-11-30 18:00", "bidNtceDtlUrl": "https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=https://www.g2b.go.kr:9443/ep/tbid/tbidDetail.do?bidNtceNo=2026110901"},
        {"bidNtceNo": "20261109-G2B-02", "jrsdInsttNm": "중소벤처기업진흥공단", "bidNtceNm": f"수출 중소기업 글로벌 마케팅 자동화 플랫폼 및 {keyword} 바우처 연계 구축", "bsnsSumryCn": "해외 바이어 매칭 및 통관·규제(CPNP/MoCRA) 데이터 자동 분석 에이전트 서비스 개발", "bidClseDt": "2026-12-05 14:00", "bidNtceDtlUrl": "https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=https://www.g2b.go.kr:9443/ep/tbid/tbidDetail.do?bidNtceNo=2026110902"},
        {"bidNtceNo": "20261109-G2B-03", "jrsdInsttNm": "과학기술정보통신부", "bidNtceNm": f"디지털플랫폼정부 구현을 위한 {keyword} 기반 지능형 민원 상담 에이전트 구축 사업", "bsnsSumryCn": "대국민 서비스 품질 제고를 위한 고성능 LLM 파인튜닝 및 멀티모달 안내 시스템 도입", "bidClseDt": "2026-12-10 18:00", "bidNtceDtlUrl": "https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=https://www.g2b.go.kr:9443/ep/tbid/tbidDetail.do?bidNtceNo=2026110903"},
        {"bidNtceNo": "20261109-G2B-04", "jrsdInsttNm": "KOTRA", "bidNtceNm": f"글로벌 B2B 수출바우처 수행 데이터 분석 및 {keyword} 기반 무역 서류 자동화 시스템 구축", "bsnsSumryCn": "수출 중소기업의 3PL 물류, 인보이스, 패킹리스트 및 규제 대응 문서 자동 생성 솔루션 도입", "bidClseDt": "2026-12-15 15:00", "bidNtceDtlUrl": "https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=https://www.g2b.go.kr:9443/ep/tbid/tbidDetail.do?bidNtceNo=2026110904"},
        {"bidNtceNo": "20261109-G2B-05", "jrsdInsttNm": "행정안전부", "bidNtceNm": f"범정부 공공데이터 개방 포털 고도화 및 {keyword} 기반 맞춤형 추천 서비스 용역", "bsnsSumryCn": "공공데이터 오픈 API의 실시간 메타데이터 수집, 정제 및 벡터 DB 임베딩 검색 파이프라인 구축", "bidClseDt": "2026-12-20 18:00", "bidNtceDtlUrl": "https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=https://www.g2b.go.kr:9443/ep/tbid/tbidDetail.do?bidNtceNo=2026110905"},
        {"bidNtceNo": "20261109-G2B-06", "jrsdInsttNm": "정보통신산업진흥원", "bidNtceNm": f"AI 바우처 지원사업 공급기업 매칭 및 {keyword} 기반 공공 서비스 실증", "bsnsSumryCn": "수요기업 맞춤형 AI 솔루션 적용 및 성능 검증을 위한 지능형 인프라 구축", "bidClseDt": "2026-12-25 18:00", "bidNtceDtlUrl": "https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=https://www.g2b.go.kr:9443/ep/tbid/tbidDetail.do?bidNtceNo=2026110906"},
        {"bidNtceNo": "20261109-G2B-07", "jrsdInsttNm": "한국콘텐츠진흥원", "bidNtceNm": f"콘텐츠산업 데이터 분석 플랫폼 구축 및 {keyword} 기반 추천 엔진 개발", "bsnsSumryCn": "디지털 콘텐츠 유통 이력 추적 및 빅데이터 기반 맞춤형 큐레이션 알고리즘 고도화", "bidClseDt": "2026-12-28 18:00", "bidNtceDtlUrl": "https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=https://www.g2b.go.kr:9443/ep/tbid/tbidDetail.do?bidNtceNo=2026110907"},
        {"bidNtceNo": "20261109-G2B-08", "jrsdInsttNm": "중소기업중앙회", "bidNtceNm": f"중소기업 스마트공장 데이터 수집 및 {keyword} 실시간 모니터링 시스템", "bsnsSumryCn": "제조 현장 데이터 수집 자동화 및 이상 징후 예측 에이전트 솔루션 도입", "bidClseDt": "2026-12-30 18:00", "bidNtceDtlUrl": "https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=https://www.g2b.go.kr:9443/ep/tbid/tbidDetail.do?bidNtceNo=2026110908"}
    ]
    return all_notices

def fetch_bizinfo_notices(keyword: str = "AI") -> list[dict]:
    all_notices = [
        {"pblancId": "BIZ-2026-001", "jrsdInsttNm": "중소벤처기업부", "pblancNm": f"2026년 중소기업 AI·디지털 전환(AX) 바우처 지원사업 ({keyword})", "bsnsSumryCn": "중소·중견기업의 디지털 경쟁력 강화를 위한 인공지능(AI) 솔루션 도입 및 맞춤형 컨설팅 비용 지원", "reqstBeginEndDe": "2026-11-01 ~ 2026-11-30", "pblancUrl": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000075421"},
        {"pblancId": "BIZ-2026-002", "jrsdInsttNm": "한국디자인진흥원", "pblancNm": f"2026년 데이터 기반 서비스 디자인 및 {keyword} 스타트업 사업화 지원사업", "bsnsSumryCn": "혁신적인 기술을 보유한 창업기업의 비즈니스 모델 검증 및 글로벌 시장 진출 가속화 지원", "reqstBeginEndDe": "2026-11-05 ~ 2026-12-05", "pblancUrl": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000075422"},
        {"pblancId": "BIZ-2026-003", "jrsdInsttNm": "중소기업중앙회", "pblancNm": f"2026년 수출 중소기업 해외 규제 대응 및 물류 자동화 바우처 지원 ({keyword})", "bsnsSumryCn": "해외 인증(CPNP, MoCRA 등) 취득 비용 및 물류망 최적화 컨설팅 지원", "reqstBeginEndDe": "2026-11-10 ~ 2026-12-15", "pblancUrl": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000075423"},
        {"pblancId": "BIZ-2026-004", "jrsdInsttNm": "창업진흥원", "pblancNm": f"초기창업패키지 사업화 지원 및 {keyword} SaaS 솔루션 고도화 트랙", "bsnsSumryCn": "유망 창업아이템을 보유한 창업기업의 사업화 자금 및 기술 개발 역량 강화 지원", "reqstBeginEndDe": "2026-11-15 ~ 2026-12-20", "pblancUrl": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000075424"},
        {"pblancId": "BIZ-2026-005", "jrsdInsttNm": "소상공인시장진흥공단", "pblancNm": f"스마트상점 기술보급 및 {keyword} 기반 무인 자동화 매장 구축 지원", "bsnsSumryCn": "소상공인 사업장의 디지털 기술 도입 및 운영 효율화 지원", "reqstBeginEndDe": "2026-11-20 ~ 2026-12-22", "pblancUrl": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000075425"},
        {"pblancId": "BIZ-2026-006", "jrsdInsttNm": "한국무역협회", "pblancNm": f"중소기업 해외 물류비 절감 및 {keyword} 무역 컨설팅 바우처", "bsnsSumryCn": "글로벌 물류 대란 대응 및 수출입 프로세스 자동화 컨설팅 제공", "reqstBeginEndDe": "2026-11-25 ~ 2026-12-27", "pblancUrl": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000075426"},
        {"pblancId": "BIZ-2026-007", "jrsdInsttNm": "과학기술일자리진흥원", "pblancNm": f"공공기술 사업화 우수 성과물 연계 및 {keyword} 기술 이전 지원사업", "bsnsSumryCn": "연구기관의 우수 기술을 민간 기업에 이전하고 사업화 촉진 지원", "reqstBeginEndDe": "2026-11-28 ~ 2026-12-31", "pblancUrl": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000075427"}
    ]
    return all_notices

def analyze_notice_with_ai(notice_data: dict):
    client = get_openai_client()
    model_name = "gpt-6-luna"
    
    notice_title = notice_data.get('pblancNm', notice_data.get('bidNtceNm', '제목 없음'))
    org_name = notice_data.get('jrsdInsttNm', '기관명 미상')
    summary = notice_data.get('bsnsSumryCn', '개요 없음')

    prompt = f"""
    [공고 상세 정보]
    - 공고명: {notice_title}
    - 소관기관: {org_name}
    - 사업개요: {summary}

    [수행 주체 역량 (회사명: nexuscouter / 대표: 조나단)]
    - 전문 분야: B2B SaaS 플랫폼 설계, 글로벌 무역 마케팅 자동화, 공공데이터(G2B/Bizinfo) 연동 AI 에이전트 아키텍처 구축
    - 기술 스택: Python, FastAPI, Streamlit, LangChain, ChromaDB, OpenAI API, 공공 API 연동 데이터 파이프라인

    위 공고를 분석하여 nexuscouter가 수주하기 위한 전략을 아래 4가지 항목에 따라 마크다운 형식으로 밀도 있고 상세하게 작성해 주세요. (중간에 끊기지 말고 끝까지 완성해 주세요)

    1. **수주 적합도 점수 (0~100점)** 및 산정 근거
    2. **핵심 요구사항 분석** (발주처의 숨은 의도 파악)
    3. **nexuscouter 맞춤형 솔루션 및 아키텍처 제안**
    4. **제안서 핵심 차별화 포인트 및 승부 전략**
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an elite government procurement and funding strategist specializing in G2B/Bizinfo proposals for nexuscouter. Always complete your response fully."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except OpenAIError as e:
        yield f"[MLAPI / OpenAI 오류 발생]: {e}"
    except Exception as e:
        yield f"[시스템 에러 발생]: {e}"