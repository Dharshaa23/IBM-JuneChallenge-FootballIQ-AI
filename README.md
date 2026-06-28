# ⚽ FootballIQ AI

**"Understand Every Match. Every Story. Every Decision."**

An AI-powered football companion built for the **IBM June Innovation Challenge**.
FootballIQ AI uses **Explainable AI** to turn football statistics, historical
records, and the Laws of the Game into clear, human-friendly explanations --
**before, during, and after** matches.

> 🚫 This project does **not** predict scores and does **not** replace referees
> or coaches. It explains football.

---

## Problem Statement

Football fans are surrounded by statistics -- possession percentages, shot
counts, head-to-head records -- but rarely get the *context* behind them.
A bare number doesn't explain why a match unfolded the way it did, or what a
rule actually means. FootballIQ AI closes that gap with grounded, transparent,
natural-language explanations.

## Objectives

- Make football statistics understandable to fans of every experience level.
- Ground every explanation in verifiable historical data and official rules.
- Demonstrate Explainable AI (XAI): transparency over black-box prediction.
- Support beginners, casual fans, and tactical analysts with adjustable depth.
- Support multiple languages so the experience is globally accessible.

## Features

| Feature | Description |
|---|---|
| 📜 **Historical Match Explainer** | Pick two teams (+ optional tournament/date) and get a full explanation of head-to-head history, key goals, and context. |
| 🔥 **Rivalry Explorer** | Deep dive into legendary rivalries: records, biggest wins, top scorers, shootout history. |
| 🔴 **Live Match Explainer** | Natural-language read on a live (or sample) match: score, possession, momentum, substitutions, tactical edge. |
| 💬 **Ask FootballIQ** | A RAG-powered chatbot grounded in the FIFA Laws of the Game and historical statistics. |
| 🎓 **Beginner / Fan / Analyst modes** | Granite adapts vocabulary and tactical depth to the chosen audience. |
| 🌐 **Multilingual** | English, Spanish, French, Hindi, Tamil. |

## Architecture

```
User Question
     │
     ▼
Historical Dataset + Football Knowledge Base + Live Match Service
     │
     ▼
Retriever  (utils/analysis.py, utils/rag.py)
     │
     ▼
Prompt Builder  (utils/prompt_builder.py)
     │
     ▼
IBM Granite  (utils/granite.py, via LangChain)
     │
     ▼
Natural Language Explanation
```

## IBM Technologies

- **IBM Granite LLM** -- core reasoning/explanation engine (via `langchain-ibm` / watsonx.ai).
- **LangChain** -- orchestrates retrieval, prompt construction, and the Granite call.
- **Docling** -- ingests football documents (FIFA Laws of the Game, glossary, rules) from PDF/DOCX/Markdown.
- **FAISS** -- vector similarity search over the ingested knowledge base for RAG.

If Granite credentials aren't configured, the app automatically runs in a
transparent **offline demo mode** (template-based fallback), so every feature
stays fully functional for evaluation without any external API calls.

## Dataset

| File | Rows | Description |
|---|---|---|
| `data/results.csv` | ~49,000 | International match results since 1872 |
| `data/goalscorers.csv` | ~47,000 | Individual goal events (scorer, minute, penalty, own goal) |
| `data/shootouts.csv` | ~680 | Penalty shootout outcomes |
| `data/former_names.csv` | ~37 | Historical team name changes (e.g. Dahomey → Benin) |

These datasets power historical explanations, head-to-head analysis, goal
scorer analysis, penalty analysis, and rivalry context -- **never** score
prediction.

## Project Structure

```
FootballIQ-AI/
├── app.py                      # Streamlit entrypoint (Home)
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── LICENSE
├── data/                       # Historical CSV datasets
├── docs/                       # Football knowledge base (FIFA rules, glossary)
├── utils/
│   ├── data_loader.py          # Loads & caches datasets
│   ├── analysis.py             # Pure statistical analysis
│   ├── match_engine.py         # Orchestration: stats + RAG + live -> prompt -> Granite
│   ├── live_match_service.py   # Live API abstraction layer (+ sample data)
│   ├── granite.py              # IBM Granite / LangChain integration
│   ├── rag.py                  # Docling ingestion + FAISS retrieval
│   ├── prompt_builder.py       # System prompts, modes, language instructions
│   └── translator.py           # Multilingual UI strings + post-hoc translation
└── pages/
    ├── 1_Historical.py         # Historical Match Explainer + Rivalry Explorer
    ├── 2_Live.py                # Live Match Explainer
    ├── 3_Chat.py                # Ask FootballIQ chatbot
    └── 4_About.py               # About / architecture / disclaimers
```

## Installation

```bash
git clone <repo-url>
cd FootballIQ-AI
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optionally add your IBM watsonx credentials
streamlit run app.py
```

## Usage

1. Launch the app and use the sidebar to navigate between pages.
2. On **Historical Match**, select two teams (and optionally a tournament/date)
   and click **Explain Match**.
3. On **Live Match**, pick a live/sample fixture and click **Explain Current Match**.
4. On **Ask FootballIQ**, ask any rules or history question in the chat box.
5. Adjust **Explanation Mode** (Beginner/Fan/Analyst) and **Language** on any page.

## Screenshots

_Add screenshots here before submission:_

- `assets/screenshot_home.png`
- `assets/screenshot_historical.png`
- `assets/screenshot_live.png`
- `assets/screenshot_chat.png`

## Future Work

- Plug in a real live-data provider (API-Football, Football-Data.org, Sportmonks).
- Ingest the full official FIFA Laws of the Game PDF via Docling.
- Add club-level (not just national team) historical datasets.
- Voice input/output for accessibility.
- Persist conversation history and favorite rivalries via SQLite.

## Team

FootballIQ AI -- IBM June Innovation Challenge submission.

## License

MIT License -- see [LICENSE](LICENSE).
