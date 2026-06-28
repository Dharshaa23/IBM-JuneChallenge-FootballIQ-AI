"""
match_engine.py
-----------------
The orchestration layer that sits between raw data (analysis.py,
live_match_service.py, rag.py) and the AI layer (granite.py, prompt_builder.py).

This is the "Retriever" + "Prompt Builder" stage of the LangChain pipeline
described in the project architecture:

    User Question -> Historical Dataset + Knowledge Base + Live Service
                   -> Retriever -> Prompt Builder -> IBM Granite -> Explanation
"""

from __future__ import annotations

from typing import Optional

from utils import analysis, prompt_builder, live_match_service as lms
from utils.granite import get_granite_client
from utils.rag import retrieve_rules_context


def explain_historical_match(
    team_a: str,
    team_b: str,
    tournament: Optional[str] = None,
    date: Optional[str] = None,
    mode: str = "Fan",
    language: str = "en",
) -> dict:
    """Run the full pipeline for the Historical Match Explainer feature."""
    h2h = analysis.compute_head_to_head(team_a, team_b, tournament)
    match_context = analysis.get_match_context(team_a, team_b, date=date, tournament=tournament)

    context_payload = {
        "head_to_head": h2h.__dict__,
        "specific_match": match_context,
    }

    prompt = prompt_builder.build_historical_prompt(context_payload, mode=mode, language=language)
    explanation = get_granite_client().generate(prompt)

    return {
        "stats": context_payload,
        "explanation": explanation,
    }


def explain_rivalry(team_a: str, team_b: str, mode: str = "Fan", language: str = "en") -> dict:
    """Run the full pipeline for the Rivalry Explorer feature."""
    h2h = analysis.compute_head_to_head(team_a, team_b)
    profile_a = analysis.compute_team_profile(team_a)
    profile_b = analysis.compute_team_profile(team_b)

    context_payload = {
        "head_to_head": h2h.__dict__,
        "team_a_profile": profile_a,
        "team_b_profile": profile_b,
    }

    prompt = prompt_builder.build_historical_prompt(context_payload, mode=mode, language=language)
    explanation = get_granite_client().generate(prompt)

    return {
        "stats": context_payload,
        "explanation": explanation,
    }


def explain_live_match(match_id: str, mode: str = "Fan", language: str = "en") -> dict:
    """Run the full pipeline for the Live Match Explainer feature."""
    provider = lms.get_live_provider()
    detail = provider.fetch_match_detail(match_id)

    if not detail:
        return {"stats": {}, "explanation": "No live match data found for that match ID."}

    enriched = dict(detail)
    enriched["possession_interpretation"] = lms.interpret_possession(detail.get("possession", {}))
    enriched["momentum_interpretation"] = lms.interpret_momentum(detail.get("momentum_last_15_min", {}))

    prompt = prompt_builder.build_live_prompt(enriched, mode=mode, language=language)
    explanation = get_granite_client().generate(prompt)

    return {
        "stats": enriched,
        "explanation": explanation,
    }


def ask_football_iq(
    question: str,
    history: list,
    mode: str = "Fan",
    language: str = "en",
    team_hint_a: Optional[str] = None,
    team_hint_b: Optional[str] = None,
) -> str:
    """Run the full RAG + stats pipeline for the Ask FootballIQ chatbot."""
    rag_context = retrieve_rules_context(question)

    stats_context = None
    if team_hint_a and team_hint_b:
        h2h = analysis.compute_head_to_head(team_hint_a, team_hint_b)
        stats_context = h2h.__dict__

    prompt = prompt_builder.build_chat_prompt(
        question=question,
        history=history,
        rag_context=rag_context,
        stats_context=stats_context,
        mode=mode,
        language=language,
    )
    return get_granite_client().generate(prompt)
