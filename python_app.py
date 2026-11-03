-- coding: utf-8 --

"""파이썬 첫걸음 - 학습 모듈 앱
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

모듈 이름을 올바른 파일명(python_content)으로 수정

from python_content import MODULES

PROGRESS_FILE = Path(file).with_name("progress.json")
ALLOW_RUN = os.getenv("ENABLE_CODE_RUN") == "1"
MARKS = "①②③"

st.set_page_config(
page_title="파이썬 첫걸음",
page_icon="🐍",
layout="centered",
initial_sidebar_state="expanded"
)

---------- 진도 저장 (단일 사용자용 JSON 파일) ----------

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
"""st.radio 라벨(마크다운)에서 _ *  $ 가 서식으로 해석되지 않게 이스케이프""" return re.sub(r"([_*$~])", r"\\1", text)

def run_code(src):
"""학습용 코드 실행 (로컬 전용). 공개 서버에서는 보안상 사용하지 마세요."""
buf = io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
try:
exec(compile(src, "", "exec"), {"name": "main"})
except Exception as e:  # noqa: BLE001
print(f"{type(e).name}: {e}")
return buf.getvalue() or "(출력 없음)"

---------- 사이드바 ----------

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

---------- 레슨 본문 ----------

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

---------- 확인 문제 ----------

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
