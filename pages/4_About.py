"""
pages/4_About.py
-------------------
About page: architecture, datasets, IBM technologies, and disclaimers.
"""

import streamlit as st

st.set_page_config(page_title="About | FootballIQ AI", page_icon="ℹ️", layout="wide")
st.title("ℹ️ About FootballIQ AI")

st.markdown(
    """
**FootballIQ AI** was built for the **IBM June Innovation Challenge** to demonstrate
a practical, explainable AI assistant for football fans -- one that explains the
game rather than trying to predict it.

### Problem Statement
Football fans are flooded with statistics but rarely get *context*. A score line or
a possession percentage rarely explains *why* a match unfolded the way it did, or
*what* a rule actually means in plain language. FootballIQ AI bridges that gap with
explainable, human-centered AI.

### Objectives
- Make football statistics understandable to fans of every experience level.
- Ground every explanation in verifiable historical data and official rules.
- Demonstrate Explainable AI (XAI) principles: transparency over black-box prediction.
- Never predict match outcomes -- explain history, rules, and live context instead.

### Architecture

```
User Question
     │
     ▼
Historical Dataset + Football Knowledge Base + Live Match Service
     │
     ▼
Retriever (analysis.py + rag.py)
     │
     ▼
Prompt Builder (prompt_builder.py)
     │
     ▼
IBM Granite (granite.py, via LangChain)
     │
     ▼
Natural Language Explanation
```

### IBM Technologies Used
- **IBM Granite LLM** -- the core reasoning and explanation engine, accessed via `langchain-ibm`.
- **LangChain** -- orchestrates retrieval, prompt construction, and the Granite call.
- **Docling** -- ingests football documents (FIFA Laws of the Game, glossary, tournament rules)
  regardless of source format (PDF, DOCX, Markdown).
- **FAISS** -- vector similarity search over the ingested knowledge base for RAG.

### Dataset
- `results.csv` -- ~49,000 international match results since 1872.
- `goalscorers.csv` -- ~47,000 individual goal events (scorer, minute, penalty, own goal).
- `shootouts.csv` -- penalty shootout outcomes.
- `former_names.csv` -- historical team name changes (e.g. Dahomey → Benin).

### Installation
```bash
git clone <repo-url>
cd FootballIQ-AI
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your IBM watsonx credentials (optional)
streamlit run app.py
```

### Usage
Navigate using the sidebar: **Historical Match**, **Live Match**, **Ask FootballIQ**.
Each page lets you choose an explanation mode (Beginner / Fan / Analyst) and a
language (English, Spanish, French, Hindi, Tamil).

> **Note:** If IBM Granite credentials are not configured in `.env`, the app runs
> in a transparent offline demo mode using a template-based fallback so every
> feature remains fully functional for evaluation.

### Future Work
- Plug in a real live-data provider (API-Football, Football-Data.org, Sportmonks).
- Ingest the full official FIFA Laws of the Game PDF via Docling.
- Add club-level (not just national team) historical datasets.
- Add voice input/output for accessibility.
- Persist conversation history and favorite rivalries via SQLite.

### Team
FootballIQ AI -- IBM June Innovation Challenge submission.

### License
MIT License -- see `LICENSE` in the repository root.
"""
)
