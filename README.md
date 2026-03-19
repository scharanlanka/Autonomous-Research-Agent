# Autonomous Research Agent

Project is now split into:

```text
.
├── backend/   # FastAPI + agent orchestration (Python)
└── frontend/  # Next.js app (port 3001)
```

## Current Status

- Streamlit UI has been removed.
- Backend now exposes FastAPI endpoints.
- Frontend is now a native Next.js app with dark/light UI.
- Agent orchestration, memory, tools, and report generation live in `backend/`.

## Backend Quickstart

1. Install deps:

```bash
cd backend
pip install -r requirements.txt
```

2. Run API:

```bash
cd ..
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8001
```

3. Open API docs:

- `http://localhost:8001/docs`

## Implemented Endpoints

- `GET /health`
- `POST /api/research/run`
- `GET /api/research/stream?query=...` (SSE progress)
- `POST /api/research/pdf`

## Frontend Quickstart

1. Install deps:

```bash
cd frontend
npm install
```

2. Run Next.js (port 3001):

```bash
npm run dev
```

3. Open:

- `http://localhost:3001`
