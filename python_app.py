# -*- coding: utf-8 -*-
"""파이썬 첫걸음 - 학습 모듈 통합 앱
실행: streamlit run python_app.py
"""
import contextlib
import io
import json
import os
import re
from pathlib import Path

import streamlit as st

# ==========================================
# 1. 학습 콘텐츠 데이터 (통합 내장)
# ==========================================
MODULES = [
    {
        "title": "1. 파이썬 코드의 기본 모양",
        "ref_name": "어휘 분석",
        "ref_url": "https://docs.python.org/ko/3.13/reference/lexical_analysis.html",
        "lessons": [
            {
                "title": "줄과 들여쓰기",
                "body": "파이썬은 들여쓰기로 코드 덩어리(블록)를 구분합니다. 중괄호 대신 공백 4칸이 관례입니다. # 뒤는 주석이라 실행되지 않습니다.",
                "code": "# 인사하기\nif True:\n    print('안녕')   # 들여쓰기 4칸\nprint('끝')",
                "tip": "같은 블록 안의 줄은 들여쓰기 칸 수가 반드시 같아야 합니다.",
                "quiz": {
                    "q": "파이썬에서 코드 블록을 구분하는 것은?",
                    "options": ["중괄호 { }", "들여쓰기", "세미콜론 ;"],
                    "answer": 1,
                    "why": "파이썬은 들여쓰기로 블록의 범위를 정합니다."
                }
            },
            {
                "title": "이름(식별자)과 키워드",
                "body": "변수나 함수에 붙이는 이름을 식별자라 합니다. 글자·숫자·밑줄(_)을 쓸 수 있지만 숫자로 시작할 수 없고, if, for 같은 키워드는 이름으로 쓸 수 없습니다. 대소문자는 구분됩니다.",
                "code": "age = 20\nAge = 30      # age와 다른 이름\n# 2nd = 1     # 오류: 숫자로 시작\n# for = 1     # 오류: 키워드",
                "tip": "이름은 user_name처럼 뜻이 보이게 짓는 것이 좋습니다.",
                "quiz": {
                    "q": "다음 중 올바른 변수 이름은?",
                    "options": ["2nd_place", "for", "my_score"],
                    "answer": 2,
                    "why": "숫자로 시작하거나 키워드인 이름은 쓸 수 없습니다."
                }
            },
            {
                "title": "숫자·문자열 리터럴",
                "body": "코드에 직접 적은 값을 리터럴이라 합니다. 정수 10, 실수 3.14, 문자열 'a' 또는 \"a\"가 대표적입니다. 여러 줄 문자열은 '''...''', 큰 수는 1_000_000처럼 밑줄로 읽기 쉽게 적을 수 있습니다.",
                "code": "print(1_000_000)   # 1000000\nprint(0xFF)        # 255 (16진수)\nprint('줄1\\n줄2')   # \\n 은 줄바꿈\nprint('a' 'b')     # ab",
                "tip": "문자열 안에 따옴표가 있으면 다른 종류의 따옴표로 감싸세요.",
                "quiz": {
                    "q": "1_000_000 은 어떤 값일까요?",
                    "options": ["오류", "백만 (1000000)", "1 과 000000"],
                    "answer": 1,
                    "why": "숫자 사이의 밑줄은 읽기 편하라고 넣는 구분자일 뿐입니다."
                }
            }
        ]
    },
    {
        "title": "2. 데이터 모델: 값과 형",
        "ref_name": "데이터 모델",
        "ref_url": "https://docs.python.org/ko/3.13/reference/datamodel.html",
        "lessons": [
            {
                "title": "모든 것은 객체",
                "body": "파이썬의 모든 데이터는 객체이고, 객체는 값(value)과 형(type)을 가집니다. type()으로 형을, id()로 객체의 고유 번호를 볼 수 있습니다.",
                "code": "print(type(3))        # <class 'int'>\nprint(type(3.5))      # <class 'float'>\nprint(type('hi'))     # <class 'str'>\nprint(type([1, 2]))   # <class 'list'>",
                "tip": "변수는 상자가 아니라 객체에 붙인 이름표라고 생각하세요.",
                "quiz": {
                    "q": "type('hi')의 결과는?",
                    "options": ["int", "str", "list"],
                    "answer": 1,
                    "why": "따옴표로 감싼 값은 문자열(str)입니다."
                }
            },
            {
                "title": "바뀌는 객체와 안 바뀌는 객체",
                "body": "리스트·딕셔너리처럼 내용을 바꿀 수 있는 객체를 가변(mutable), 숫자·문자열·튜플처럼 바꿀 수 없는 객체를 불변(immutable)이라 합니다.",
                "code": "a = [1, 2]\nb = a          # 같은 객체를 가리킴\nb.append(3)\nprint(a)       # [1, 2, 3]",
                "tip": "복사본이 필요하면 b = a.copy()를 쓰세요.",
                "quiz": {
                    "q": "a=[1,2]; b=a; b.append(3) 후 a의 값은?",
                    "options": ["[1, 2]", "[1, 2, 3]", "[3]"],
                    "answer": 1,
                    "why": "a와 b는 같은 리스트 객체를 가리키므로 함께 바뀝니다."
                }
            }
        ]
    }
]

# ==========================================
# 2. 애플리케이션 로직 및 UI 설정
# ==========================================
PROGRESS_FILE = Path(__file__).with_name("progress.json")
ALLOW_RUN = os.getenv("ENABLE_CODE_RUN") == "1"
MARKS = "①②③"

st.set_page_config(page_title="파이썬 첫걸음", page_icon="🐍", layout="centered")

def load_done():
    try:
        return set(json.loads(PROGRESS_FILE.read_text(encoding="utf-8")).get("done", []))
    except Exception:
        return set()

def save_done():
    try:
        PROGRESS_FILE.write_text(json.dumps({"done": sorted(list(st.session_state.done))}, ensure_ascii=False), encoding="utf-8")
    except Exception:
        st.warning("진도를 파일에 저장하지 못했습니다.")

if "done" not in st.session_state:
    st.session_state.done = load_done()
DONE = st.session_state.done

def esc(text):
    return re.sub(r"([_*`$~])", r"\\\1", text)

def run_code(src):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            exec(compile(src, "<lesson>", "exec"), {"__name__": "__main__"})
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
    return buf.getvalue() or "(출력 없음)"

# 사이드바
total = sum(len(m["lessons"]) for m in MODULES)
st.sidebar.title("🐍 파이썬 첫걸음")
st.sidebar.progress(len(DONE) / total if total > 0 else 0, text=f"진도 {len(DONE)} / {total} 레슨")

mi = st.sidebar.selectbox("모듈", range(len(MODULES)), format_func=lambda i: MODULES[i]["title"])
module = MODULES[mi]
li = st.sidebar.selectbox(
    "레슨", range(len(module["lessons"])),
    format_func=lambda j: ("✓ " if f"{mi}-{j}" in DONE else "") + module["lessons"][j]["title"],
    key=f"lesson-{mi}",
)
lesson = module["lessons"][li]
lid = f"{mi}-{li}"

if st.sidebar.button("진도 초기화"):
    DONE.clear()
    save_done()
    st.rerun()

# 레슨 본문
st.caption(f"레퍼런스: [{module['ref_name']} ↗]({module['ref_url']})")
st.header(lesson["title"])
st.html(f"<div style='line-height:1.8'>{lesson['body']}</div>")

st.subheader("예제 코드")
st.code(lesson["code"], language="python")
st.html(f"<div style='background:rgba(55,118,171,.14);padding:10px 14px;border-radius:8px'>💡 {lesson['tip']}</div>")

if ALLOW_RUN:
    with st.expander("▶ 직접 실행해 보기"):
        src = st.text_area("코드를 고쳐서 실행해 보세요", lesson["code"], height=200, key=f"src-{lid}")
        if st.button("실행", key=f"run-{lid}"):
            st.code(run_code(src), language="text")

# 확인 문제
st.subheader("확인 문제")
quiz = lesson["quiz"]
with st.form(f"quiz-{lid}"):
    choice = st.radio(
        esc(quiz["q"]), range(len(quiz["options"])), index=None,
        format_func=lambda k: f"{MARKS[k]} {esc(quiz['options'][k])}",
        key=f"radio-{lid}",
    )
    submitted = st.form_submit_button("정답 확인", type="primary")

if submitted:
    if choice is None:
        st.warning("답을 선택해 주세요.")
    elif choice == quiz["answer"]:
        st.success(f"정답입니다! {quiz['why']}")
        if lid not in DONE:
            DONE.add(lid)
            save_done()
            st.balloons()
    else:
        st.error("아쉬워요, 다시 골라 보세요.")
elif lid in DONE:
    st.success("✓ 이미 완료한 레슨입니다.")

st.divider()
st.caption("이 콘텐츠는 파이썬 언어 레퍼런스를 참고해 새로 작성했습니다. Python 문서 © Python Software Foundation (PSF License v2).")
