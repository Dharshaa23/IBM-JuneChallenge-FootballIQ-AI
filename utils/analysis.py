"""
analysis.py
------------
Pure statistical analysis over the historical datasets. This module computes
numbers ONLY -- it never generates natural language. Natural language
explanation is the job of granite.py + prompt_builder.py. Keeping this
separation makes the analysis testable and the AI layer swappable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from utils.data_loader import load_results, load_goalscorers, load_shootouts


@dataclass
class HeadToHeadStats:
    team_a: str
    team_b: str
    total_matches: int = 0
    team_a_wins: int = 0
    team_b_wins: int = 0
    draws: int = 0
    team_a_goals: int = 0
    team_b_goals: int = 0
    avg_goals_per_match: float = 0.0
    biggest_team_a_win: Optional[dict] = None
    biggest_team_b_win: Optional[dict] = None
    penalty_shootouts: int = 0
    team_a_shootout_wins: int = 0
    team_b_shootout_wins: int = 0
    top_scorers: list = field(default_factory=list)
    tournaments: dict = field(default_factory=dict)
    recent_meetings: list = field(default_factory=list)
    first_meeting_date: Optional[str] = None
    last_meeting_date: Optional[str] = None
    neutral_venue_matches: int = 0


def _matches_between(df: pd.DataFrame, team_a: str, team_b: str) -> pd.DataFrame:
    mask = (
        ((df["home_team"] == team_a) & (df["away_team"] == team_b))
        | ((df["home_team"] == team_b) & (df["away_team"] == team_a))
    )
    return df[mask].sort_values("date")


def compute_head_to_head(team_a: str, team_b: str, tournament: Optional[str] = None) -> HeadToHeadStats:
    """Compute full head-to-head statistics between two teams."""
    results = load_results()
    stats = HeadToHeadStats(team_a=team_a, team_b=team_b)

    if results.empty:
        return stats

    matches = _matches_between(results, team_a, team_b)
    if tournament:
        matches = matches[matches["tournament"] == tournament]

    if matches.empty:
        return stats

    stats.total_matches = len(matches)
    stats.first_meeting_date = str(matches["date"].min().date()) if pd.notna(matches["date"].min()) else None
    stats.last_meeting_date = str(matches["date"].max().date()) if pd.notna(matches["date"].max()) else None
    stats.neutral_venue_matches = int(matches["neutral"].sum())

    biggest_a_margin, biggest_b_margin = -1, -1

    for _, row in matches.iterrows():
        home, away = row["home_team"], row["away_team"]
        hs, as_ = row["home_score"], row["away_score"]

        a_score = hs if home == team_a else as_
        b_score = as_ if home == team_a else hs

        stats.team_a_goals += int(a_score)
        stats.team_b_goals += int(b_score)

        if a_score > b_score:
            stats.team_a_wins += 1
            margin = a_score - b_score
            if margin > biggest_a_margin:
                biggest_a_margin = margin
                stats.biggest_team_a_win = {
                    "date": str(row["date"].date()) if pd.notna(row["date"]) else "unknown",
                    "score": f"{a_score}-{b_score}",
                    "tournament": row["tournament"],
                }
        elif b_score > a_score:
            stats.team_b_wins += 1
            margin = b_score - a_score
            if margin > biggest_b_margin:
                biggest_b_margin = margin
                stats.biggest_team_b_win = {
                    "date": str(row["date"].date()) if pd.notna(row["date"]) else "unknown",
                    "score": f"{a_score}-{b_score}",
                    "tournament": row["tournament"],
                }
        else:
            stats.draws += 1

        tname = row["tournament"]
        stats.tournaments[tname] = stats.tournaments.get(tname, 0) + 1

    stats.avg_goals_per_match = round((stats.team_a_goals + stats.team_b_goals) / max(stats.total_matches, 1), 2)

    # Recent meetings (last 5, most recent first)
    recent = matches.sort_values("date", ascending=False).head(5)
    stats.recent_meetings = [
        {
            "date": str(r["date"].date()) if pd.notna(r["date"]) else "unknown",
            "home_team": r["home_team"],
            "away_team": r["away_team"],
            "score": f"{r['home_score']}-{r['away_score']}",
            "tournament": r["tournament"],
        }
        for _, r in recent.iterrows()
    ]

    # Penalty shootouts
    shootouts = load_shootouts()
    if not shootouts.empty:
        so_matches = _matches_between(shootouts, team_a, team_b)
        stats.penalty_shootouts = len(so_matches)
        stats.team_a_shootout_wins = int((so_matches["winner"] == team_a).sum())
        stats.team_b_shootout_wins = int((so_matches["winner"] == team_b).sum())

    # Top scorers in these fixtures
    goalscorers = load_goalscorers()
    if not goalscorers.empty:
        gs_matches = goalscorers[
            ((goalscorers["home_team"] == team_a) & (goalscorers["away_team"] == team_b))
            | ((goalscorers["home_team"] == team_b) & (goalscorers["away_team"] == team_a))
        ]
        if not gs_matches.empty:
            top = gs_matches["scorer"].dropna().value_counts().head(5)
            stats.top_scorers = [{"name": name, "goals": int(count)} for name, count in top.items()]

    return stats


def compute_team_profile(team: str) -> dict:
    """Compute a general statistical profile for a single team across all history."""
    results = load_results()
    if results.empty:
        return {}

    home = results[results["home_team"] == team]
    away = results[results["away_team"] == team]

    wins = int(((home["home_score"] > home["away_score"]).sum()) + ((away["away_score"] > away["home_score"]).sum()))
    losses = int(((home["home_score"] < home["away_score"]).sum()) + ((away["away_score"] < away["home_score"]).sum()))
    draws = int(((home["home_score"] == home["away_score"]).sum()) + ((away["away_score"] == away["home_score"]).sum()))
    goals_for = int(home["home_score"].sum() + away["away_score"].sum())
    goals_against = int(home["away_score"].sum() + away["home_score"].sum())
    total = wins + losses + draws

    tournament_counts = pd.concat([home["tournament"], away["tournament"]]).value_counts().head(5).to_dict()

    return {
        "team": team,
        "total_matches": total,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "win_rate": round(wins / total * 100, 1) if total else 0.0,
        "top_tournaments": tournament_counts,
    }


def get_match_context(team_a: str, team_b: str, date: Optional[str] = None, tournament: Optional[str] = None) -> dict:
    """
    Find a specific match (or the closest match) between two teams and return
    its full statistical context, including the goal-by-goal breakdown.
    """
    results = load_results()
    if results.empty:
        return {}

    matches = _matches_between(results, team_a, team_b)
    if tournament:
        matches = matches[matches["tournament"] == tournament]
    if matches.empty:
        return {}

    if date:
        target = pd.to_datetime(date, errors="coerce")
        if pd.notna(target):
            matches = matches.copy()
            matches["_diff"] = (matches["date"] - target).abs()
            match_row = matches.sort_values("_diff").iloc[0]
        else:
            match_row = matches.sort_values("date", ascending=False).iloc[0]
    else:
        match_row = matches.sort_values("date", ascending=False).iloc[0]

    goalscorers = load_goalscorers()
    goals = []
    if not goalscorers.empty:
        match_goals = goalscorers[
            (goalscorers["date"] == match_row["date"])
            & (goalscorers["home_team"] == match_row["home_team"])
            & (goalscorers["away_team"] == match_row["away_team"])
        ].sort_values("minute")
        goals = [
            {
                "minute": g["minute"],
                "scorer": g["scorer"],
                "team": g["team"],
                "penalty": bool(g.get("penalty", False)),
                "own_goal": bool(g.get("own_goal", False)),
            }
            for _, g in match_goals.iterrows()
        ]

    return {
        "date": str(match_row["date"].date()) if pd.notna(match_row["date"]) else "unknown",
        "home_team": match_row["home_team"],
        "away_team": match_row["away_team"],
        "home_score": int(match_row["home_score"]),
        "away_score": int(match_row["away_score"]),
        "tournament": match_row["tournament"],
        "city": match_row.get("city", "unknown"),
        "country": match_row.get("country", "unknown"),
        "neutral": bool(match_row.get("neutral", False)),
        "goals": goals,
    }
