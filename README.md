# Autonomous Research Agent (ARA)

An end-to-end research system that plans a topic, gathers evidence from web + arXiv sources, drafts a report, critiques it, and returns a refined final output through a streaming UX.

## Highlights

- Multi-agent research workflow built with LangGraph
- Live progress streaming via Server-Sent Events (SSE)
- Source-aware report generation with iterative refinement
- Persistent memory using ChromaDB for cross-run recall
- PDF export for generated reports
- Clean Next.js interface with light/dark theming

## Architecture

- `frontend/`: Next.js App Router client (port `3001`)
- `backend/`: FastAPI API + agent orchestration (port `8001`)
- `chroma_db/`: Local vector memory persistence

Detailed flow is documented in [`Architecture.md`](/Users/saicharanlanka/Education/Autonomous%20Research%20Agent/Architecture.md).

## Tech Stack

- Frontend: Next.js 16, React 18, TypeScript
- Backend: FastAPI, LangGraph, Pydantic
- Retrieval: Tavily, DuckDuckGo tooling, arXiv
- Memory: ChromaDB + Azure embeddings
- LLM: Azure-hosted chat model integration

## Prerequisites

- Node.js `18+` (or `20+` recommended)
- npm
- Python `3.13+`
- pip (or `uv` if preferred)

## Environment Setup

Create a root `.env` file (already loaded automatically by backend config) with:

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

For frontend API routing, create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
```

## Quickstart

1. Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

2. Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

3. Start backend (from repo root):

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8001
```

4. Start frontend (new terminal):

```bash
cd frontend
npm run dev
```

5. Open the app:

- Frontend: `http://localhost:3001`
- API docs: `http://localhost:8001/docs`

## Core API Endpoints

- `GET /health`
- `POST /api/research/run`
- `GET /api/research/stream?query=...`
- `POST /api/research/pdf`

## Repository Structure

```text
.
├── backend/
│   ├── app.py
│   └── ara/
├── frontend/
│   ├── app/
│   └── components/
├── chroma_db/
├── Architecture.md
└── README.md
```
