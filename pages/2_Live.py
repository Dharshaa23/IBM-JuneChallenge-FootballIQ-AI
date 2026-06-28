"""
pages/2_Live.py
------------------
Live Match Explainer -- score, possession, momentum, substitutions, tactics.

Works fully offline with realistic sample data via the LiveMatchProvider
abstraction in utils/live_match_service.py. Plug in a real API key in .env
to switch to live data without changing this file.
"""

import streamlit as st

from utils.live_match_service import get_live_provider
from utils.match_engine import explain_live_match

st.set_page_config(page_title="Live Match | FootballIQ AI", page_icon="🔴", layout="wide")
st.title("🔴 Live Match Explainer")
st.caption("Understand what's happening right now -- score, possession, momentum, and tactics. No score predictions.")

provider = get_live_provider()
live_matches = provider.fetch_live_matches()

if not live_matches:
    st.info("No live matches available right now. Try again later, or configure a live data provider in .env.")
    st.stop()

match_options = {f"{m['home_team']} vs {m['away_team']} ({m['tournament']}) -- {m['minute']}'": m["match_id"] for m in live_matches}
selected_label = st.selectbox("Select a live match (sample data shown if no API key is configured)", list(match_options.keys()))
match_id = match_options[selected_label]

mode_col, lang_col = st.columns(2)
with mode_col:
    mode = st.radio("Explanation Mode", ["Beginner", "Fan", "Analyst"], horizontal=True, index=1)
with lang_col:
    language = st.selectbox(
        "Language",
        options=["en", "es", "fr", "hi", "ta"],
        format_func=lambda c: {"en": "English", "es": "Español", "fr": "Français", "hi": "हिन्दी", "ta": "தமிழ்"}[c],
    )

if st.button("⚡ Explain Current Match", type="primary"):
    with st.spinner("Reading live match data and consulting IBM Granite..."):
        try:
            result = explain_live_match(match_id, mode=mode, language=language)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Something went wrong while analyzing this live match: {exc}")
        else:
            stats = result["stats"]

            st.subheader(f"⏱️ {stats['home_team']} {stats['home_score']} - {stats['away_score']} {stats['away_team']} ({stats['minute']}')")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Possession**")
                st.progress(stats["possession"]["home"] / 100, text=f"{stats['home_team']}: {stats['possession']['home']}%")
                st.progress(stats["possession"]["away"] / 100, text=f"{stats['away_team']}: {stats['possession']['away']}%")
            with c2:
                st.markdown("**Shots (on target)**")
                st.write(f"{stats['home_team']}: {stats['shots']['home']} ({stats['shots_on_target']['home']})")
                st.write(f"{stats['away_team']}: {stats['shots']['away']} ({stats['shots_on_target']['away']})")
            with c3:
                st.markdown("**Momentum (last 15 min)**")
                st.write(f"{stats['home_team']}: {stats['momentum_last_15_min']['home']}%")
                st.write(f"{stats['away_team']}: {stats['momentum_last_15_min']['away']}%")
                st.caption(f"Tag: {stats['momentum_interpretation']}")

            st.subheader("📋 Match Timeline")
            for event in stats.get("events", []):
                icon = {"goal": "⚽", "yellow_card": "🟨", "red_card": "🟥", "substitution": "🔄"}.get(event["type"], "•")
                team_name = stats["home_team"] if event["team"] == "home" else stats["away_team"]
                if event["type"] == "substitution":
                    st.write(f"{icon} {event['minute']}' -- {team_name}: {event['player_in']} ON, {event['player_out']} OFF")
                else:
                    st.write(f"{icon} {event['minute']}' -- {team_name}: {event.get('player', '')}")

            st.subheader("🧠 FootballIQ Explanation")
            st.markdown(result["explanation"])

            with st.expander("Raw live data used (transparency)"):
                st.json(stats)
