# -*- coding: utf-8 -*-
"""영어 읽기 학습 모듈 (문법·어휘·유형 공략·플래시카드)
실행: streamlit run toeic_app.py
"""
import json
import random
from pathlib import Path

import streamlit as st

# toeic_content 파일명에 맞게 import 수정
from toeic_content import GRAMMAR, STRATEGY, VOCAB

PROGRESS_FILE = Path(__file__).with_name("progress.json")
LABELS = "ABCD"
SECTIONS = {"📗 문법": ("grammar", GRAMMAR), "📘 어휘": ("vocab", VOCAB), "🎯 유형 공략": ("strategy", STRATEGY)}

st.set_page_config(page_title="영어 읽기 학습 모듈", page_icon="📘", layout="centered")


# ---------- 진도 저장 (단일 사용자용 JSON 파일) ----------
def load_progress():
    try:
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        return {"done": data.get("done", []), "known": data.get("known", [])}
    except Exception:
        return {"done": [], "known": []}


def save_progress():
    try:
        PROGRESS_FILE.write_text(json.dumps(st.session_state.p, ensure_ascii=False), encoding="utf-8")
    except Exception:
        st.warning("진도를 파일에 저장하지 못했습니다.")


if "p" not in st.session_state:
    st.session_state.p = load_progress()
P = st.session_state.p


def lesson_id(sec, i):
    return f"{sec}-{i}"


# ---------- 레슨 화면 ----------
def show_lesson(sec, i, lesson):
    lid = lesson_id(sec, i)
    st.header(lesson["t"])
    if lesson.get("b"):
        st.markdown(lesson["b"])
    if lesson.get("words"):
        st.table([{"단어": w, "뜻": m, "자주 쓰는 표현": c} for w, m, c in lesson["words"]])
    for en, ko in lesson.get("ex", []):
        st.markdown(f"> **{en}**  \n> {ko}")
    if lesson.get("tip"):
        st.info("💡 " + lesson["tip"])

    st.subheader("문제 풀이")
    with st.form(f"form-{lid}"):
        for n, (q, opts, _, _) in enumerate(lesson["qs"]):
            st.radio(f"{n + 1}. {q}", [f"({LABELS[k]}) {o}" for k, o in enumerate(opts)],
                     index=None, key=f"{lid}-q{n}")
        submitted = st.form_submit_button("정답 확인", type="primary")

    if submitted:
        all_ok = True
        for n, (q, opts, ans, why) in enumerate(lesson["qs"]):
            sel = st.session_state.get(f"{lid}-q{n}")
            if sel is None:
                all_ok = False
                st.warning(f"{n + 1}번: 답을 선택해 주세요.")
            elif sel.startswith(f"({LABELS[ans]})"):
                st.success(f"{n + 1}번 정답! {why}")
            else:
                all_ok = False
                st.error(f"{n + 1}번 오답입니다. 설명을 다시 읽고 도전해 보세요.")
        if all_ok and lid not in P["done"]:
            P["done"].append(lid)
            save_progress()
            st.balloons()
        if all_ok:
            st.success("🎉 레슨 완료!")


def lesson_page(label):
    sec, lessons = SECTIONS[label]
    names = [("✓ " if lesson_id(sec, i) in P["done"] else "") + l["t"] for i, l in enumerate(lessons)]
    idx = st.selectbox("레슨 선택", range(len(lessons)), format_func=lambda k: names[k], key=f"sel-{sec}")
    st.divider()
    show_lesson(sec, idx, lessons[idx])


# ---------- 플래시카드 ----------
def flashcards():
    st.header("🃏 어휘 플래시카드")
    sel = st.selectbox("카드 묶음", ["전체"] + [l["t"] for l in VOCAB])
    hide = st.checkbox("외운 카드 제외", value=True)
    cards = [c for l in VOCAB if sel in ("전체", l["t"]) for c in l["words"]]
    if hide:
        cards = [c for c in cards if c[0] not in P["known"]]

    sig = (sel, hide)
    if st.session_state.get("fc_sig") != sig:
        st.session_state.update(fc_sig=sig, fc_deck=list(cards), fc_i=0, fc_flip=False)
    deck = st.session_state.fc_deck
    if not deck:
        st.success("이 묶음의 카드를 모두 외웠어요! 🎉")
        return
    i = st.session_state.fc_i % len(deck)
    word, meaning, colloc = deck[i]

    st.progress((i + 1) / len(deck), text=f"{i + 1} / {len(deck)}")
    with st.container(border=True):
        if st.session_state.fc_flip:
            st.markdown(f"<h2 style='text-align:center'>{meaning}</h2>"
                        f"<p style='text-align:center'>예: <i>{colloc}</i></p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='text-align:center;padding:1rem 0'>{word}</h1>", unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("⬅ 이전", use_container_width=True):
        st.session_state.update(fc_i=(i - 1) % len(deck), fc_flip=False)
        st.rerun()
    if c2.button("🔄 뒤집기", use_container_width=True):
        st.session_state.fc_flip = not st.session_state.fc_flip
        st.rerun()
    if c3.button("➡ 다음", use_container_width=True):
        st.session_state.update(fc_i=(i + 1) % len(deck), fc_flip=False)
        st.rerun()
    if c4.button("✅ 외웠어요", use_container_width=True):
        if word not in P["known"]:
            P["known"].append(word)
            save_progress()
        deck.pop(i)
        st.session_state.update(fc_i=i, fc_flip=False)
        st.rerun()
    if c5.button("🔀 섞기", use_container_width=True):
        random.shuffle(deck)
        st.session_state.update(fc_i=0, fc_flip=False)
        st.rerun()
    st.caption(f"외운 단어: {len(P['known'])}개")


# ---------- 홈 ----------
def home():
    st.title("📘 영어 읽기 학습 모듈")
    st.write("직장 영어 중심의 **문법·어휘** 학습 앱입니다. 설명 → 예문 → 문제 풀이 순서로 진행하세요.")
    total_words = sum(len(l["words"]) for l in VOCAB)
    for label, (sec, lessons) in SECTIONS.items():
        n = sum(lesson_id(sec, i) in P["done"] for i in range(len(lessons)))
        st.progress(n / len(lessons), text=f"{label}  {n} / {len(lessons)} 레슨 완료")
    st.metric("외운 단어", f"{len(P['known'])} / {total_words}")
    if st.button("진도 초기화"):
        P["done"].clear()
        P["known"].clear()
        save_progress()
        st.rerun()


# ---------- 메인 ----------
MENU = ["🏠 홈"] + list(SECTIONS) + ["🃏 플래시카드"]
page = st.sidebar.radio("메뉴", MENU)
if page == "🏠 홈":
    home()
elif page == "🃏 플래시카드":
    flashcards()
else:
    lesson_page(page)
st.sidebar.caption("모든 설명과 문항은 오리지널로 작성되었습니다.")
