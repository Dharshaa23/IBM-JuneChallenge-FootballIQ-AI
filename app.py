"""
app.py
-------
FootballIQ AI -- main Streamlit entrypoint.

"Understand Every Match. Every Story. Every Decision."

This file sets up global page config, theming, and the sidebar navigation.
Each feature lives in its own file under pages/ (Streamlit's native
multi-page app convention), so app.py itself stays small and just renders
the Home / landing experience.
"""

import streamlit as st

from utils.granite import get_granite_client

st.set_page_config(
    page_title="FootballIQ AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
# Theme: dark mode, green pitch palette
# --------------------------------------------------------------------------- #
CUSTOM_CSS = """
<style>
:root {
    --pitch-green: #1b5e20;
    --pitch-green-light: #2e7d32;
    --accent: #76ff03;
    --bg-dark: #0e1410;
    --card-bg: #14201a;
}
.stApp {
    background: linear-gradient(180deg, #0e1410 0%, #0c1810 100%);
    color: #eafff0;
}
section[data-testid="stSidebar"] {
    background-color: #0a120c;
    border-right: 1px solid #1f3b27;
}
h1, h2, h3 {
    color: #d8ffe0;
}
.fiq-card {
    background-color: var(--card-bg);
    border: 1px solid #1f3b27;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.fiq-tagline {
    color: var(--accent);
    font-size: 1.1rem;
    font-style: italic;
}
.fiq-pill {
    display: inline-block;
    background: var(--pitch-green-light);
    color: white;
    border-radius: 999px;
    padding: 0.2rem 0.8rem;
    font-size: 0.8rem;
    margin-right: 0.4rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #
st.title("⚽ FootballIQ AI")
st.markdown('<p class="fiq-tagline">"Understand Every Match. Every Story. Every Decision."</p>', unsafe_allow_html=True)

granite_status = "🟢 IBM Granite connected" if get_granite_client().is_live() else "🟡 Offline demo mode (template fallback)"
st.markdown(
    f'<span class="fiq-pill">{granite_status}</span>'
    '<span class="fiq-pill">Explainable AI</span>'
    '<span class="fiq-pill">Not a predictor</span>',
    unsafe_allow_html=True,
)

st.markdown("---")

# --------------------------------------------------------------------------- #
# Intro cards
# --------------------------------------------------------------------------- #
col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown(
        """
        <div class="fiq-card">
        <h3>What is FootballIQ AI?</h3>
        <p>FootballIQ AI is an AI-powered football companion built for the
        <b>IBM June Innovation Challenge</b>. It uses <b>IBM Granite</b>,
        orchestrated with <b>LangChain</b>, to turn raw football statistics,
        historical records, and the FIFA Laws of the Game into clear,
        human-friendly explanations.</p>
        <p><b>This is not a score predictor.</b> FootballIQ AI never tells you
        who will win. Instead, it helps you understand <i>why</i> things
        happened, <i>why</i> they matter, and <i>what</i> the rules say --
        before, during, and after a match.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="fiq-card">
        <h3>Explore the app</h3>
        <ul>
        <li><b>📜 Historical Match</b> -- explain any historical fixture, head-to-head record, and tournament context.</li>
        <li><b>🔥 Rivalry Explorer</b> -- dive deep into legendary rivalries like Argentina vs Brazil.</li>
        <li><b>🔴 Live Match</b> -- get a natural-language read on a live (or sample) match: score, possession, momentum, tactics.</li>
        <li><b>💬 Ask FootballIQ</b> -- a conversational assistant grounded in football rules and statistics.</li>
        <li><b>ℹ️ About</b> -- architecture, datasets, and IBM technologies used.</li>
        </ul>
        <p>Use the sidebar to navigate. Choose your <b>explanation mode</b>
        (Beginner / Fan / Analyst) and <b>language</b> on each page to tailor
        the AI's response style.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="fiq-card" style="text-align:center;">
        <div style="font-size:5rem;">⚽</div>
        <h3>Explainable. Educational. Human-centered.</h3>
        <p>Every explanation is grounded in real statistics from over 49,000
        historical international matches, 47,000+ individual goals, and the
        official Laws of the Game -- with full transparency into the
        evidence behind every answer.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="fiq-card">
        <h4>IBM Technologies</h4>
        <p>🧠 IBM Granite LLM<br>
        🔗 LangChain orchestration<br>
        📄 Docling document ingestion<br>
        🔍 FAISS vector retrieval (RAG)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.caption(
    "FootballIQ AI · Built for the IBM June Innovation Challenge · "
    "Use the sidebar to navigate to Historical Match, Live Match, or Ask FootballIQ."
)
