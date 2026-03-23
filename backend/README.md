# Backend API

FastAPI + LangGraph backend for the Autonomous Research Agent. It handles query orchestration, tool calls, report generation, memory operations, and PDF export.

## What It Does

- Accepts research queries through REST endpoints
- Streams live execution events (`progress`, `plan`, `source`, `log`, `result`)
- Runs a multi-step pipeline: planner -> memory retrieve -> researcher -> summarizer -> critic -> memory store
- Persists compact research memory in ChromaDB
- Exposes PDF report export endpoint

## Tech Stack

- Python 3.13+
- FastAPI + Uvicorn
- LangGraph / LangChain Core
- ChromaDB
- Tavily + arXiv tools
- ReportLab (PDF generation)

## Required Environment Variables

Backend loads `.env` from the repository root automatically.

```bash
AZURE_LLM_ENDPOINT=
AZURE_LLM_API_KEY=
AZURE_LLM_DEPLOYMENT_NAME=

AZURE_EMBEDDING_ENDPOINT=
AZURE_EMBEDDING_API_KEY=
AZURE_EMBEDDING_DEPLOYMENT_NAME=

TAVILY_API_KEY=

CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION=ara_memory
DDG_MAX_RESULTS=8
ARXIV_MAX_RESULTS=5
FETCH_MAX_CHARS=12000
TAVILY_MAX_RESULTS=8
```

## Setup

1. Install dependencies from project root:

```bash
pip install -r backend/requirements.txt
```

2. Run API server (from project root):

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8001
```

Alternative entrypoint:

```bash
python -m backend.main
```

3. Open interactive docs:

- `http://localhost:8001/docs`

## API Endpoints

- `GET /health`
- `POST /api/research/run`
- `GET /api/research/stream?query=...`
- `POST /api/research/pdf`

## Request Examples

`POST /api/research/run`

```json
{
  "query": "Research the impact of AI on software engineering jobs from 2023 to 2026."
}
```

`POST /api/research/pdf`

```json
{
  "title": "ARA Research Report",
  "markdown_text": "# Report\n\n..."
}
```

## Project Layout

```text
backend/
├── app.py
├── main.py
├── requirements.txt
└── ara/
    ├── graph.py
    ├── memory.py
    ├── config.py
    ├── agents/
    └── tools/
```
