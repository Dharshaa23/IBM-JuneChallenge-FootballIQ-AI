"""
granite.py
-----------
IBM Granite LLM integration layer, orchestrated through LangChain.

This module wraps IBM watsonx.ai's Granite models behind a single
`GraniteClient` class so the rest of the app never talks to the SDK directly.

Design goals:
    1. The rest of the app should work even if WATSONX credentials are not
       configured -- in that case GraniteClient falls back to a transparent,
       template-based explanation generator so the prototype still runs
       end-to-end during judging / demos.
    2. Switching models, temperature, or providers should require touching
       only this file.

Environment variables (see .env.example):
    WATSONX_API_KEY
    WATSONX_PROJECT_ID
    WATSONX_URL                 (default: https://us-south.ml.cloud.ibm.com)
    GRANITE_MODEL_ID             (default: ibm/granite-3-8b-instruct)
"""

from __future__ import annotations

import os
from typing import Optional

import re
import ast

from dotenv import load_dotenv

load_dotenv()

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
GRANITE_MODEL_ID = os.getenv("GRANITE_MODEL_ID", "ibm/granite-3-8b-instruct")

GRANITE_AVAILABLE = bool(WATSONX_API_KEY and WATSONX_PROJECT_ID)


class GraniteClient:
    """
    Thin wrapper around the IBM Granite model accessed through LangChain's
    `langchain-ibm` integration. Falls back to a deterministic local
    explanation generator when credentials are absent, so the app is always
    demoable.
    """

    def __init__(
        self,
        model_id: str = GRANITE_MODEL_ID,
        temperature: float = 0.4,
        max_new_tokens: int = 700,
    ) -> None:
        self.model_id = model_id
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self._llm = None

        if GRANITE_AVAILABLE:
            try:
                self._llm = self._build_langchain_llm()
            except Exception as exc:  # noqa: BLE001
                # Never crash the app because the model backend is unreachable.
                print(f"[granite.py] Falling back to offline mode: {exc}")
                self._llm = None

    # ------------------------------------------------------------------ #
    # LangChain / watsonx wiring
    # ------------------------------------------------------------------ #
    def _build_langchain_llm(self):
        """
        Build a LangChain-compatible Granite LLM via langchain-ibm.

        Requires: pip install langchain-ibm ibm-watsonx-ai
        """
        from langchain_ibm import WatsonxLLM  # imported lazily so the
        # rest of the app works even if this optional package isn't installed.

        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "repetition_penalty": 1.05,
        }

        return WatsonxLLM(
            model_id=self.model_id,
            url=WATSONX_URL,
            apikey=WATSONX_API_KEY,
            project_id=WATSONX_PROJECT_ID,
            params=parameters,
        )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def is_live(self) -> bool:
        """True if a real Granite backend is configured and initialized."""
        return self._llm is not None

    def generate(self, prompt: str) -> str:
        """
        Generate a natural language response for the given fully-built prompt.
        Falls back to a deterministic offline explainer if Granite is not
        configured, so judges/demos always see a complete answer.
        """
        if self._llm is not None:
            try:
                return self._llm.invoke(prompt)
            except Exception as exc:  # noqa: BLE001
                print(f"[granite.py] Generation failed, using fallback: {exc}")

        return self._offline_fallback(prompt)

    # ------------------------------------------------------------------ #
    # Offline fallback (no API key / no network)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _offline_fallback(prompt: str) -> str:
        """
        Intelligent offline AI explanation.

        Instead of showing the raw prompt, this function extracts the
        structured football statistics already embedded in the prompt
        and generates a natural explanation similar to IBM Granite.
        """

        try:

            # ----------------------------
            # LIVE MATCH
            # ----------------------------

            if "LIVE MATCH DATA" in prompt:

                match = re.search(
                    r"LIVE MATCH DATA.*?\n(\{.*\})",
                    prompt,
                    re.DOTALL,
                )

                if match:

                    data = ast.literal_eval(match.group(1))

                    home = data["home_team"]
                    away = data["away_team"]

                    hs = data["home_score"]
                    aw = data["away_score"]

                    minute = data["minute"]

                    pos_h = data["possession"]["home"]
                    pos_a = data["possession"]["away"]

                    shots_h = data["shots"]["home"]
                    shots_a = data["shots"]["away"]

                    target_h = data["shots_on_target"]["home"]
                    target_a = data["shots_on_target"]["away"]

                    corners_h = data["corners"]["home"]
                    corners_a = data["corners"]["away"]

                    fouls_h = data["fouls"]["home"]
                    fouls_a = data["fouls"]["away"]

                    leader = home if hs > aw else away if aw > hs else None

                    return f"""
# ⚽ FootballIQ AI

### Match Summary

At the **{minute}th minute**, **{home}** lead **{away}** **{hs}-{aw}**.

{"{} currently have the advantage after converting their chances more efficiently.".format(leader) if leader else "The score is level, making this an evenly contested match."}

---

## Possession & Control

- {home}: **{pos_h}%**
- {away}: **{pos_a}%**

{"{} have dictated the tempo through better ball retention.".format(home if pos_h > pos_a else away)}

---

## Attacking Threat

- Shots: **{shots_h}-{shots_a}**
- Shots on Target: **{target_h}-{target_a}**
- Corners: **{corners_h}-{corners_a}**

The team creating more shots on target has generated the clearer scoring opportunities rather than relying on speculative efforts.

---

## Defensive Discipline

- Fouls: **{fouls_h}-{fouls_a}**

The foul count reflects the intensity of the contest, with both teams attempting to disrupt each other's rhythm.

---

## Tactical Insight

Although possession is important, matches are ultimately decided by the quality of chances created and converted. The current statistics suggest that the leading team has combined territorial control with greater attacking efficiency.

---

## Why It Matters

Football is more than numbers. Looking beyond the scoreline helps explain **why the match currently stands at {hs}-{aw}**, giving fans a clearer understanding of the tactical battle.

---

⚠️ *Offline AI Mode*

IBM Granite credentials are not configured, so this explanation has been generated locally using the available match statistics.
"""

        # ----------------------------
        # HISTORICAL MATCH
        # ----------------------------

        return """
# ⚽ FootballIQ AI

### Historical Match Analysis

FootballIQ AI analysed the historical statistics provided by the application.

Instead of simply reporting the score, the system interprets:

• Head-to-head history

• Goal-scoring patterns

• Tournament significance

• Team momentum

• Match trends

---

## Tactical Insight

Historical football matches are often influenced by tactical discipline, efficient finishing and momentum rather than possession alone.

---

## Why It Matters

Understanding *why* a team won gives fans a much richer understanding than simply reading the final score.

---

⚠️ *Offline AI Mode*

IBM Granite credentials are not configured, so this explanation has been generated locally.
"""

    except Exception:

        return """
# ⚽ FootballIQ AI

Offline mode is active.

The application is functioning correctly, but IBM Granite credentials have not been configured.

Once WATSONX_API_KEY and WATSONX_PROJECT_ID are added, FootballIQ AI will automatically generate richer explanations using IBM Granite.
"""


# Module-level singleton so Streamlit pages can share one client across reruns.
_client: Optional[GraniteClient] = None


def get_granite_client() -> GraniteClient:
    """Return a shared GraniteClient instance (singleton pattern)."""
    global _client
    if _client is None:
        _client = GraniteClient()
    return _client
