"""
pages/3_Chat.py
------------------
Ask FootballIQ -- conversational chatbot grounded in the football knowledge
base (RAG over FIFA Laws of the Game via Docling + FAISS) and historical
statistics.
"""

import streamlit as st

from utils.data_loader import get_all_team_names
from utils.match_engine import ask_football_iq

st.set_page_config(page_title="Ask FootballIQ | FootballIQ AI", page_icon="💬", layout="wide")
st.title("💬 Ask FootballIQ")
st.caption("Ask anything about football rules, history, or a specific rivalry. Powered by RAG + IBM Granite.")

teams = ["(none)"] + get_all_team_names()

with st.sidebar:
    st.markdown("### Chat Settings")
    mode = st.radio("Explanation Mode", ["Beginner", "Fan", "Analyst"], index=1)
    language = st.selectbox(
        "Language",
        options=["en", "es", "fr", "hi", "ta"],
        format_func=lambda c: {"en": "English", "es": "Español", "fr": "Français", "hi": "हिन्दी", "ta": "தமிழ்"}[c],
    )
    st.markdown("**Optional: ground answers in a specific rivalry**")
    team_a = st.selectbox("Team A", teams, key="chat_team_a")
    team_b = st.selectbox("Team B", teams, key="chat_team_b")
    if st.button("Clear conversation"):
        st.session_state.chat_history = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown("##### Try asking:")
example_cols = st.columns(3)
examples = ["Explain offside.", "Why was that own goal controversial?", "Who dominated midfield in a high-pressing game?"]
for col, ex in zip(example_cols, examples):
    with col:
        if st.button(ex, use_container_width=True):
            st.session_state["_pending_question"] = ex

for turn in st.session_state.chat_history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

pending = st.session_state.pop("_pending_question", None)
user_question = pending or st.chat_input("Ask FootballIQ about rules, history, or rivalries...")

if user_question:
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the knowledge base and consulting IBM Granite..."):
            hint_a = None if team_a == "(none)" else team_a
            hint_b = None if team_b == "(none)" else team_b
            try:
                answer = ask_football_iq(
                    user_question,
                    history=st.session_state.chat_history,
                    mode=mode,
                    language=language,
                    team_hint_a=hint_a,
                    team_hint_b=hint_b,
                )
            except Exception as exc:  # noqa: BLE001
                answer = f"Sorry, something went wrong answering that: {exc}"
            st.markdown(answer)

    st.session_state.chat_history.append({"role": "assistant", "content": answer})
