"""
translator.py
---------------
Multilingual support for FootballIQ AI.

The primary path uses IBM Granite itself (through granite.py) to translate
or directly generate explanations in the target language -- Granite models
are multilingual, so for most languages it is simplest (and highest quality)
to instruct Granite to respond directly in the target language via
prompt_builder's language block, rather than translating after the fact.

This module exists for the cases where a *post-hoc* translation of an
already-generated English explanation is needed (e.g. translating cached
content, or translating UI strings).
"""

from __future__ import annotations

from utils.granite import get_granite_client

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "hi": "Hindi",
    "ta": "Tamil",
}

# Minimal static UI string translations (avoids an LLM round-trip for labels).
UI_STRINGS = {
    "en": {
        "select_team_a": "Select Team A",
        "select_team_b": "Select Team B",
        "explain_match": "Explain Match",
        "explanation_mode": "Explanation Mode",
        "language": "Language",
    },
    "es": {
        "select_team_a": "Selecciona Equipo A",
        "select_team_b": "Selecciona Equipo B",
        "explain_match": "Explicar Partido",
        "explanation_mode": "Modo de Explicación",
        "language": "Idioma",
    },
    "fr": {
        "select_team_a": "Sélectionner l'Équipe A",
        "select_team_b": "Sélectionner l'Équipe B",
        "explain_match": "Expliquer le Match",
        "explanation_mode": "Mode d'Explication",
        "language": "Langue",
    },
    "hi": {
        "select_team_a": "टीम A चुनें",
        "select_team_b": "टीम B चुनें",
        "explain_match": "मैच समझाएं",
        "explanation_mode": "व्याख्या मोड",
        "language": "भाषा",
    },
    "ta": {
        "select_team_a": "அணி A தேர்ந்தெடுக்கவும்",
        "select_team_b": "அணி B தேர்ந்தெடுக்கவும்",
        "explain_match": "ஆட்டத்தை விளக்கு",
        "explanation_mode": "விளக்க முறை",
        "language": "மொழி",
    },
}


def get_ui_string(key: str, lang_code: str = "en") -> str:
    """Return a UI label in the requested language, falling back to English."""
    return UI_STRINGS.get(lang_code, UI_STRINGS["en"]).get(key, UI_STRINGS["en"].get(key, key))


def translate_text(text: str, target_lang_code: str) -> str:
    """
    Translate already-generated text into the target language using Granite.
    Used sparingly -- prefer generating directly in the target language via
    prompt_builder when possible, since that produces more natural output.
    """
    if target_lang_code == "en":
        return text

    lang_name = SUPPORTED_LANGUAGES.get(target_lang_code, "English")
    prompt = (
        f"Translate the following football analysis into {lang_name}. "
        "Preserve all statistics, names, and meaning exactly. "
        "Return only the translation, nothing else.\n\n"
        f"---\n{text}\n---"
    )
    return get_granite_client().generate(prompt)
