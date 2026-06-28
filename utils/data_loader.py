"""
data_loader.py
----------------
Loads and caches the historical football datasets used throughout FootballIQ AI.

Datasets:
    - results.csv        : Match results (date, teams, scores, tournament, venue)
    - goalscorers.csv     : Individual goal events (scorer, minute, penalty, own goal)
    - shootouts.csv       : Penalty shootout results
    - former_names.csv    : Historical team name changes (e.g. Dahomey -> Benin)

All loaders return pandas DataFrames with normalized dtypes and are wrapped with
streamlit caching where streamlit is available, falling back to a no-op cache
decorator otherwise (e.g. when used from a plain script or test).
"""

from __future__ import annotations

import os
from typing import Optional

import pandas as pd

try:
    import streamlit as st
    _cache = st.cache_data
except Exception:  # streamlit not installed / running outside streamlit
    def _cache(func=None, **_kwargs):
        if func is None:
            return lambda f: f
        return func

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

RESULTS_PATH = os.path.join(DATA_DIR, "results.csv")
GOALSCORERS_PATH = os.path.join(DATA_DIR, "goalscorers.csv")
SHOOTOUTS_PATH = os.path.join(DATA_DIR, "shootouts.csv")
FORMER_NAMES_PATH = os.path.join(DATA_DIR, "former_names.csv")


def _safe_read_csv(path: str) -> pd.DataFrame:
    """Read a CSV file, returning an empty DataFrame with a warning if missing."""
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@_cache
def load_results() -> pd.DataFrame:
    """Load historical match results."""
    df = _safe_read_csv(RESULTS_PATH)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["home_score"] = pd.to_numeric(df["home_score"], errors="coerce").fillna(0).astype(int)
    df["away_score"] = pd.to_numeric(df["away_score"], errors="coerce").fillna(0).astype(int)
    df["neutral"] = df["neutral"].astype(str).str.upper() == "TRUE"
    df["year"] = df["date"].dt.year
    return df


@_cache
def load_goalscorers() -> pd.DataFrame:
    """Load individual goal-scoring events."""
    df = _safe_read_csv(GOALSCORERS_PATH)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ("own_goal", "penalty"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.upper() == "TRUE"
    return df


@_cache
def load_shootouts() -> pd.DataFrame:
    """Load penalty shootout results."""
    df = _safe_read_csv(SHOOTOUTS_PATH)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


@_cache
def load_former_names() -> pd.DataFrame:
    """Load historical team name changes."""
    return _safe_read_csv(FORMER_NAMES_PATH)


def resolve_team_name(name: str) -> str:
    """
    Resolve a possibly historical team name to its current name using
    former_names.csv (e.g. 'Dahomey' -> 'Benin'). If no match is found,
    the original name is returned unchanged.
    """
    former = load_former_names()
    if former.empty:
        return name
    match = former[former["former"].str.lower() == name.lower()]
    if not match.empty:
        return match.iloc[0]["current"]
    return name


def get_all_team_names() -> list[str]:
    """Return a sorted, de-duplicated list of all team names that appear in results.csv."""
    df = load_results()
    if df.empty:
        return []
    teams = pd.concat([df["home_team"], df["away_team"]]).dropna().unique().tolist()
    return sorted(teams)


def get_all_tournaments() -> list[str]:
    """Return a sorted, de-duplicated list of tournament names."""
    df = load_results()
    if df.empty:
        return []
    return sorted(df["tournament"].dropna().unique().tolist())
