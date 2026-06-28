"""
live_match_service.py
------------------------
Abstraction layer for live football data providers.

This module defines a `LiveMatchProvider` interface so that any real
football API (API-Football, Football-Data.org, Sportmonks, etc.) can be
plugged in later by implementing `fetch_live_matches()` and
`fetch_match_detail()` without touching any other part of the app.

Until a provider is configured (via LIVE_FOOTBALL_API_KEY in .env), the
service transparently falls back to realistic sample JSON data so every
feature -- score, possession, momentum, substitutions, tactics -- can be
demoed end-to-end offline.
"""

from __future__ import annotations

import os
import random
from abc import ABC, abstractmethod
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

LIVE_FOOTBALL_API_KEY = os.getenv("LIVE_FOOTBALL_API_KEY", "")
LIVE_FOOTBALL_PROVIDER = os.getenv("LIVE_FOOTBALL_PROVIDER", "sample")  # "api-football" | "football-data" | "sportmonks" | "sample"


# ---------------------------------------------------------------------------
# Provider interface
# ---------------------------------------------------------------------------
class LiveMatchProvider(ABC):
    """Interface every live football data provider must implement."""

    @abstractmethod
    def fetch_live_matches(self) -> list[dict]:
        """Return a list of currently live matches (lightweight summaries)."""

    @abstractmethod
    def fetch_match_detail(self, match_id: str) -> dict:
        """Return full detail for a single match: score, stats, events, lineups."""


# ---------------------------------------------------------------------------
# Sample / offline provider (default, always works)
# ---------------------------------------------------------------------------
class SampleMatchProvider(LiveMatchProvider):
    """
    Provides deterministic sample live-match data so the app is fully
    demoable without any API key. Swap LIVE_FOOTBALL_PROVIDER in .env to use
    a real provider once credentials are available.
    """

    SAMPLE_MATCHES = [
        {
            "match_id": "sample-1",
            "home_team": "Argentina",
            "away_team": "Brazil",
            "tournament": "Copa America (Sample)",
            "minute": 67,
            "status": "LIVE",
            "home_score": 2,
            "away_score": 1,
            "possession": {"home": 58, "away": 42},
            "shots": {"home": 11, "away": 7},
            "shots_on_target": {"home": 6, "away": 3},
            "corners": {"home": 5, "away": 3},
            "fouls": {"home": 8, "away": 12},
            "events": [
                {"minute": 12, "type": "goal", "team": "home", "player": "L. Martinez"},
                {"minute": 38, "type": "yellow_card", "team": "away", "player": "E. Militao"},
                {"minute": 55, "type": "goal", "team": "away", "player": "Vinicius Jr."},
                {"minute": 61, "type": "substitution", "team": "home", "player_in": "A. Garnacho", "player_out": "A. Di Maria"},
                {"minute": 63, "type": "goal", "team": "home", "player": "J. Alvarez"},
                {"minute": 66, "type": "substitution", "team": "away", "player_in": "Rodrygo", "player_out": "Raphinha"},
            ],
            "momentum_last_15_min": {"home": 70, "away": 30},
        },
        {
            "match_id": "sample-2",
            "home_team": "France",
            "away_team": "Germany",
            "tournament": "International Friendly (Sample)",
            "minute": 24,
            "status": "LIVE",
            "home_score": 0,
            "away_score": 0,
            "possession": {"home": 47, "away": 53},
            "shots": {"home": 3, "away": 5},
            "shots_on_target": {"home": 1, "away": 2},
            "corners": {"home": 1, "away": 2},
            "fouls": {"home": 4, "away": 3},
            "events": [
                {"minute": 9, "type": "yellow_card", "team": "home", "player": "A. Tchouameni"},
            ],
            "momentum_last_15_min": {"home": 40, "away": 60},
        },
    ]

    def fetch_live_matches(self) -> list[dict]:
        return [
            {
                "match_id": m["match_id"],
                "home_team": m["home_team"],
                "away_team": m["away_team"],
                "tournament": m["tournament"],
                "minute": m["minute"],
                "status": m["status"],
                "score": f"{m['home_score']}-{m['away_score']}",
            }
            for m in self.SAMPLE_MATCHES
        ]

    def fetch_match_detail(self, match_id: str) -> dict:
        for m in self.SAMPLE_MATCHES:
            if m["match_id"] == match_id:
                return m
        return {}


# ---------------------------------------------------------------------------
# Real provider stubs (implement when API keys are available)
# ---------------------------------------------------------------------------
class ApiFootballProvider(LiveMatchProvider):
    """
    Stub for https://www.api-football.com/ integration.
    Implement fetch_live_matches/fetch_match_detail using `requests` against
    the API-Football REST endpoints once LIVE_FOOTBALL_API_KEY is set.
    """

    BASE_URL = "https://v3.football.api-sports.io"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_live_matches(self) -> list[dict]:
        # import requests
        # headers = {"x-apisports-key": self.api_key}
        # resp = requests.get(f"{self.BASE_URL}/fixtures", params={"live": "all"}, headers=headers)
        # return _normalize_api_football_fixtures(resp.json())
        raise NotImplementedError("Plug in your API-Football key and implement the request above.")

    def fetch_match_detail(self, match_id: str) -> dict:
        raise NotImplementedError("Plug in your API-Football key and implement the request above.")


class FootballDataProvider(LiveMatchProvider):
    """Stub for https://www.football-data.org/ integration."""

    BASE_URL = "https://api.football-data.org/v4"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_live_matches(self) -> list[dict]:
        raise NotImplementedError("Plug in your Football-Data.org key and implement the request.")

    def fetch_match_detail(self, match_id: str) -> dict:
        raise NotImplementedError("Plug in your Football-Data.org key and implement the request.")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
def get_live_provider() -> LiveMatchProvider:
    """Return the configured live match provider, falling back to sample data."""
    if LIVE_FOOTBALL_PROVIDER == "api-football" and LIVE_FOOTBALL_API_KEY:
        return ApiFootballProvider(LIVE_FOOTBALL_API_KEY)
    if LIVE_FOOTBALL_PROVIDER == "football-data" and LIVE_FOOTBALL_API_KEY:
        return FootballDataProvider(LIVE_FOOTBALL_API_KEY)
    return SampleMatchProvider()


# ---------------------------------------------------------------------------
# Derived interpretation helpers (used by match_engine.py)
# ---------------------------------------------------------------------------
def interpret_possession(possession: dict) -> str:
    """Return a short structured tag describing possession dominance."""
    home, away = possession.get("home", 50), possession.get("away", 50)
    diff = abs(home - away)
    if diff < 5:
        return "balanced"
    leader = "home" if home > away else "away"
    if diff >= 20:
        return f"{leader}_dominant"
    return f"{leader}_slight_edge"


def interpret_momentum(momentum: dict) -> str:
    """Return a short structured tag describing recent momentum."""
    home, away = momentum.get("home", 50), momentum.get("away", 50)
    diff = abs(home - away)
    if diff < 10:
        return "even"
    leader = "home" if home > away else "away"
    return f"{leader}_building"
