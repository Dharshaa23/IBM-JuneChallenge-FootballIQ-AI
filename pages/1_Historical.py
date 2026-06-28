"""
pages/1_Historical.py
------------------------
Historical Match Explainer + Rivalry Explorer.
"""

import streamlit as st

from utils.data_loader import get_all_team_names, get_all_tournaments
from utils.match_engine import explain_historical_match, explain_rivalry

st.set_page_config(page_title="Historical Match | FootballIQ AI", page_icon="📜", layout="wide")
st.title("📜 Historical Match & Rivalry Explorer")
st.caption("Explain historical fixtures and legendary rivalries using real match data -- not predictions.")

teams = get_all_team_names()
tournaments = ["Any tournament"] + get_all_tournaments()

tab1, tab2 = st.tabs(["🏟️ Historical Match Explainer", "🔥 Rivalry Explorer"])

# --------------------------------------------------------------------------- #
# Tab 1: Historical Match Explainer
# --------------------------------------------------------------------------- #
with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        team_a = st.selectbox("Select Team A", teams, index=teams.index("Argentina") if "Argentina" in teams else 0, key="hist_team_a")
    with col2:
        team_b = st.selectbox("Select Team B", teams, index=teams.index("Brazil") if "Brazil" in teams else 1, key="hist_team_b")
    with col3:
        tournament = st.selectbox("Tournament", tournaments, key="hist_tournament")

    date_input = st.text_input("Specific date (optional, YYYY-MM-DD) -- leave blank for the most recent meeting", key="hist_date")

    mode_col, lang_col = st.columns(2)
    with mode_col:
        mode = st.radio("Explanation Mode", ["Beginner", "Fan", "Analyst"], horizontal=True, index=1, key="hist_mode")
    with lang_col:
        language = st.selectbox(
            "Language",
            options=["en", "es", "fr", "hi", "ta"],
            format_func=lambda c: {"en": "English", "es": "Español", "fr": "Français", "hi": "हिन्दी", "ta": "தமிழ்"}[c],
            key="hist_lang",
        )

    if st.button("⚡ Explain Match", type="primary", key="hist_explain_btn"):
        if team_a == team_b:
            st.warning("Please select two different teams.")
        else:
            with st.spinner("Analyzing historical statistics and consulting IBM Granite..."):
                try:
                    tourn_filter = None if tournament == "Any tournament" else tournament
                    result = explain_historical_match(
                        team_a, team_b,
                        tournament=tourn_filter,
                        date=date_input or None,
                        mode=mode,
                        language=language,
                    )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Something went wrong while analyzing this match: {exc}")
                else:
                    h2h = result["stats"]["head_to_head"]
                    specific = result["stats"]["specific_match"]

                    st.subheader("📊 Head-to-Head Statistics")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric(f"{team_a} wins", h2h.get("team_a_wins", 0))
                    c2.metric(f"{team_b} wins", h2h.get("team_b_wins", 0))
                    c3.metric("Draws", h2h.get("draws", 0))
                    c4.metric("Total matches", h2h.get("total_matches", 0))

                    if specific:
                        st.subheader("🎯 Closest Matching Fixture")
                        st.write(
                            f"**{specific['home_team']} {specific['home_score']} - "
                            f"{specific['away_score']} {specific['away_team']}** · "
                            f"{specific['tournament']} · {specific['date']} · {specific.get('city', '')}"
                        )
                        if specific.get("goals"):
                            with st.expander("Goal-by-goal breakdown"):
                                for g in specific["goals"]:
                                    tag = " (pen)" if g["penalty"] else " (OG)" if g["own_goal"] else ""
                                    st.write(f"⚽ {g['minute']}' -- {g['scorer']} ({g['team']}){tag}")

                    st.subheader("🧠 FootballIQ Explanation")
                    st.markdown(result["explanation"])

                    with st.expander("Raw statistics used (transparency)"):
                        st.json(result["stats"])

# --------------------------------------------------------------------------- #
# Tab 2: Rivalry Explorer
# --------------------------------------------------------------------------- #
with tab2:
    st.markdown("Explore legendary rivalries in depth -- full history, biggest wins, top scorers, and why fans love it.")
    col1, col2 = st.columns(2)
    with col1:
        riv_a = st.selectbox("Select Team A", teams, index=teams.index("Argentina") if "Argentina" in teams else 0, key="riv_team_a")
    with col2:
        riv_b = st.selectbox("Select Team B", teams, index=teams.index("Brazil") if "Brazil" in teams else 1, key="riv_team_b")

    mode_col2, lang_col2 = st.columns(2)
    with mode_col2:
        riv_mode = st.radio("Explanation Mode", ["Beginner", "Fan", "Analyst"], horizontal=True, index=1, key="riv_mode")
    with lang_col2:
        riv_lang = st.selectbox(
            "Language",
            options=["en", "es", "fr", "hi", "ta"],
            format_func=lambda c: {"en": "English", "es": "Español", "fr": "Français", "hi": "हिन्दी", "ta": "தமிழ்"}[c],
            key="riv_lang",
        )

    if st.button("🔥 Explore Rivalry", type="primary", key="riv_explore_btn"):
        if riv_a == riv_b:
            st.warning("Please select two different teams.")
        else:
            with st.spinner("Digging through history and consulting IBM Granite..."):
                try:
                    result = explain_rivalry(riv_a, riv_b, mode=riv_mode, language=riv_lang)
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Something went wrong while analyzing this rivalry: {exc}")
                else:
                    h2h = result["stats"]["head_to_head"]

                    st.subheader(f"⚔️ {riv_a} vs {riv_b}")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric(f"{riv_a} wins", h2h.get("team_a_wins", 0))
                    c2.metric(f"{riv_b} wins", h2h.get("team_b_wins", 0))
                    c3.metric("Draws", h2h.get("draws", 0))
                    c4.metric("Penalty shootouts", h2h.get("penalty_shootouts", 0))

                    if h2h.get("top_scorers"):
                        st.markdown("**Top scorers in this fixture:**")
                        st.table(h2h["top_scorers"])

                    if h2h.get("recent_meetings"):
                        st.markdown("**Recent meetings:**")
                        for m in h2h["recent_meetings"]:
                            st.write(f"- {m['date']}: {m['home_team']} {m['score']} {m['away_team']} ({m['tournament']})")

                    st.subheader("🧠 FootballIQ Explanation")
                    st.markdown(result["explanation"])

                    with st.expander("Raw statistics used (transparency)"):
                        st.json(result["stats"])
