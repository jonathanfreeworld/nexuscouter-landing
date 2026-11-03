-- coding: utf-8 --

"""파이썬 첫걸음 - 학습 모듈 통합 앱
실행: streamlit run python_app.py
(선택) 코드 실습 기능: ENABLE_CODE_RUN=1 streamlit run python_app.py   ※ 로컬 학습용, 공개 서버에서는 사용 금지
"""
import contextlib
import io
import json
import os
import re
from pathlib import Path

import streamlit as st

==========================================

1. 학습 콘텐츠 데이터 (python_content 내장 통합)

==========================================

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
"body": "코드에 직접 적은 값을 리터럴이라 합니다. 정수 10, 실수 3.14, 문자열 'a' 또는 "a"가 대표적입니다. 여러 줄 문자열은 '''...''', 큰 수는 1_000_000처럼 밑줄로 읽기 쉽게 적을 수 있습니다.",
"code": "print(1_000_000)   # 1000000\nprint(0xFF)        # 255 (16진수)\nprint('줄1\n줄2')   # \n 은 줄바꿈\nprint('a' 'b')     # ab",
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
"body": "리스트·딕셔너리처럼 내용을 바꿀 수 있는 객체를 가변(mutable), 숫자·문자열·튜플처럼 바꿀 수 없는 객체를 불변(immutable)이라 합니다. 두 이름이 같은 가변 객체를 가리키면 한쪽을 바꿀 때 다른 쪽도 바뀝니다.",
"code": "a = [1, 2]\nb = a          # 같은 객체를 가리킴\nb.append(3)\nprint(a)       # [1, 2, 3]\n\ns = 'abc'\n# s[0] = 'x'   # 오류: 문자열은 불변",
"tip": "복사본이 필요하면 b = a.copy()를 쓰세요.",
"quiz": {
"q": "a=[1,2]; b=a; b.append(3) 후 a의 값은?",
"options": ["[1, 2]", "[1, 2, 3]", "[3]"],
"answer": 1,
"why": "a와 b는 같은 리스트 객체를 가리키므로 함께 바뀝니다."
}
},
{
"title": "리스트·튜플·딕셔너리·집합",
"body": "데이터를 묶는 기본 그릇 4가지입니다. 리스트 [ ]는 순서가 있고 변경 가능, 튜플 ( )은 변경 불가, 딕셔너리 {키: 값}은 키로 값을 찾고, 집합 { }은 중복을 자동으로 제거합니다.",
"code": "scores = [90, 80]\nscores.append(70)\npoint = (3, 4)\nuser = {'name': '민수', 'age': 20}\nprint(user['name'])   # 민수\nprint({1, 2, 2, 3})   # {1, 2, 3}",
"tip": "순서가 중요하면 리스트, 이름표로 찾으려면 딕셔너리를 쓰세요.",
"quiz": {
"q": "user = {'name': '민수'} 에서 '민수'를 꺼내는 방법은?",
"options": ["user['name']", "user.name", "user(name)"],
"answer": 0,
"why": "딕셔너리는 대괄호 안에 키를 넣어 값을 꺼냅니다."
}
}
]
},
{
"title": "3. 표현식과 연산자",
"ref_name": "표현식",
"ref_url": "https://docs.python.org/ko/3.13/reference/expressions.html",
"lessons": [
{
"title": "산술과 비교 연산",
"body": "표현식은 계산하면 값이 되는 코드입니다. /는 나눗셈(실수), //는 몫, %는 나머지, 는 거듭제곱입니다. 비교 결과는 True/False입니다.",
"code": "print(7 / 2)    # 3.5\nprint(7 // 2)   # 3\nprint(7 % 2)    # 1\nprint(2  10)  # 1024\nprint(1 < 3 < 5)  # True",
"tip": "1 < 3 < 5처럼 비교를 이어 쓸 수 있는 것은 파이썬의 특징입니다.",
"quiz": {
"q": "17 // 5 의 값은?",
"options": ["3", "3.4", "2"],
"answer": 0,
"why": "// 는 나눗셈의 몫만 구합니다. 17을 5로 나눈 몫은 3입니다."
}
},
{
"title": "논리 연산과 우선순위",
"body": "and, or, not으로 조건을 조합합니다. 연산자에는 우선순위가 있어  → 곱셈·나눗셈 → 덧셈·뺄셈 → 비교 → not → and → or 순으로 계산됩니다. 헷갈리면 괄호를 쓰세요.",
"code": "print(2 + 3 * 4)     # 14\nprint((2 + 3) * 4)   # 20\nprint(True or False and False)  # True",
"tip": "가독성을 위해 괄호를 아끼지 마세요.",
"quiz": {
"q": "2 + 3 * 4 의 값은?",
"options": ["20", "14", "24"],
"answer": 1,
"why": "곱셈이 덧셈보다 먼저 계산되어 2 + 12 = 14가 됩니다."
}
},
{
"title": "리스트 컴프리헨션",
"body": "반복문으로 리스트를 만드는 코드를 한 줄로 줄이는 표현식입니다. 모양은 [식 for 변수 in 시퀀스 if 조건]입니다.",
"code": "squares = [n * n for n in range(5)]\nprint(squares)   # [0, 1, 4, 9, 16]\nevens = [n for n in range(10) if n % 2 == 0]\nprint(evens)     # [0, 2, 4, 6, 8]",
"tip": "너무 복잡해지면 일반 for 문으로 풀어 쓰는 편이 읽기 좋습니다.",
"quiz": {
"q": "[n * 2 for n in range(3)] 의 결과는?",
"options": ["[0, 2, 4]", "[2, 4, 6]", "[0, 1, 2]"],
"answer": 0,
"why": "n이 0, 1, 2일 때 각각 2배하면 0, 2, 4입니다."
}
}
]
}
]

==========================================

2. 애플리케이션 로직 및 UI 설정

==========================================

PROGRESS_FILE = Path(file).with_name("progress.json")
ALLOW_RUN = os.getenv("ENABLE_CODE_RUN") == "1"
MARKS = "①②③"

st.set_page_config(
page_title="파이썬 첫걸음",
page_icon="🐍",
layout="centered",
initial_sidebar_state="expanded"
)

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
return re.sub(r"([_*`$~])", r"\\1", text)

def run_code(src):
buf = io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
try:
exec(compile(src, "", "exec"), {"name": "main"})
except Exception as e:
print(f"{type(e).name}: {e}")
return buf.getvalue() or "(출력 없음)"

사이드바

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

레슨 본문

st.caption(f"레퍼런스: {module['ref_name']} ↗")
st.header(lesson["title"])
st.html(f"{lesson['body']}")

st.subheader("예제 코드")
st.code(lesson["code"], language="python")
st.html(f"💡 {lesson['tip']}")

if ALLOW_RUN:
with st.expander("▶ 직접 실행해 보기"):
src = st.text_area("코드를 고쳐서 실행해 보세요", lesson["code"], height=200, key=f"src-{lid}")
if st.button("실행", key=f"run-{lid}"):
st.code(run_code(src), language="text")

확인 문제

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
