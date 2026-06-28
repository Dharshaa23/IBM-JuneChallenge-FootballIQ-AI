"""
prompt_builder.py
-------------------
Builds the final prompts sent to IBM Granite. Centralizing prompt
construction here makes the system prompt, explanation modes, and
language instructions consistent across every page of the app.
"""

from __future__ import annotations

from typing import Optional

SYSTEM_PROMPT = """You are FootballIQ AI, an expert football (soccer) analyst and educator.

Your job is to EXPLAIN football, never to predict it.

Core rules:
- Never simply repeat statistics back to the user. Always explain WHY something
  happened, WHY it matters, and WHAT fans should understand from it.
- Be accurate and ground every claim in the statistics provided to you. Never invent
  facts, players, or scores that are not present in the provided context.
- Never predict future match outcomes or scores. If asked to predict, politely
  redirect to historical explanation instead.
- Be warm, clear, and engaging -- like a knowledgeable friend explaining the game,
  not a stats sheet.
"""

MODE_INSTRUCTIONS = {
    "Beginner": (
        "Explain using simple, everyday language. Avoid tactical jargon entirely. "
        "Assume the reader is new to football and explain any rule or term you use."
    ),
    "Fan": (
        "Use normal football terminology (e.g. clean sheet, derby, knockout stage) "
        "as a knowledgeable fan would, but keep sentences clear and energetic."
    ),
    "Analyst": (
        "Use tactical depth: discuss formations, pressing, transitions, space, "
        "tempo, and momentum shifts. Assume the reader understands the game deeply."
    ),
}

LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "hi": "Hindi",
    "ta": "Tamil",
}


def _mode_block(mode: str) -> str:
    return MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["Fan"])


def _language_block(lang_code: str) -> str:
    name = LANGUAGE_NAMES.get(lang_code, "English")
    if lang_code == "en":
        return ""
    return f"\nRespond entirely in {name}. Do not mix in English unless quoting a proper noun.\n"


def build_historical_prompt(context: dict, mode: str = "Fan", language: str = "en") -> str:
    """Build a prompt for the Historical Match Explainer / Rivalry Explorer."""
    return f"""{SYSTEM_PROMPT}

EXPLANATION MODE: {mode}
{_mode_block(mode)}
{_language_block(language)}

MATCH / RIVALRY STATISTICS (ground truth -- do not contradict these numbers):
{context}

TASK:
Using only the statistics above, write a engaging explanation that covers:
1. The historical context and importance of this fixture/rivalry.
2. The head-to-head record and what it reveals.
3. Notable goals, penalties, or shootouts.
4. Why this matchup matters to fans.
Keep it well-organized with short paragraphs or bullet points where useful.
"""


def build_live_prompt(live_data: dict, mode: str = "Fan", language: str = "en") -> str:
    """Build a prompt for the Live Match Explainer."""
    return f"""{SYSTEM_PROMPT}

EXPLANATION MODE: {mode}
{_mode_block(mode)}
{_language_block(language)}

LIVE MATCH DATA (ground truth -- do not contradict these numbers):
{live_data}

TASK:
Explain the current state of this match to a fan who just tuned in, covering:
1. The current score and what it means in context.
2. Possession and momentum -- who is controlling the game and why.
3. Key events so far (goals, substitutions, cards) and their impact.
4. Which team currently holds the tactical advantage, and why.
Do NOT predict the final result. Focus purely on explaining what has happened
and what it means right now.
"""


def build_chat_prompt(
    question: str,
    history: list,
    rag_context: Optional[str] = None,
    stats_context: Optional[dict] = None,
    mode: str = "Fan",
    language: str = "en",
) -> str:
    """Build a prompt for the conversational Ask FootballIQ chatbot."""
    history_block = ""
    if history:
        formatted = "\n".join(f"{turn['role'].upper()}: {turn['content']}" for turn in history[-6:])
        history_block = f"\nRECENT CONVERSATION:\n{formatted}\n"

    rag_block = f"\nRELEVANT FOOTBALL RULES / KNOWLEDGE BASE EXCERPTS:\n{rag_context}\n" if rag_context else ""
    stats_block = f"\nRELEVANT STATISTICS:\n{stats_context}\n" if stats_context else ""

    return f"""{SYSTEM_PROMPT}

EXPLANATION MODE: {mode}
{_mode_block(mode)}
{_language_block(language)}
{history_block}{rag_block}{stats_block}

USER QUESTION:
{question}

TASK:
Answer the user's question naturally and accurately, grounding your answer in the
knowledge base excerpts and/or statistics above when they are relevant. If the
question is about a rule, explain it clearly with an example. If you don't have
enough information to answer confidently, say so honestly rather than guessing.
"""
