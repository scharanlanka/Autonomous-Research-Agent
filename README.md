# Autonomous Research Agent (ARA) - Streamlit v1

## Run
1) Create venv and install:
   pip install -r requirements.txt

2) Create `.env` using `.env.example` format.

3) Start:
   streamlit run app.py

## What v1 includes
- LangGraph multi-agent orchestration
- Planner → Research → Summarize → Critic → Memory
- DuckDuckGo search (free) + arXiv search
- Page fetching + text extraction
- ChromaDB memory using Azure embeddings
- Structured report with citations
- Markdown + PDF export