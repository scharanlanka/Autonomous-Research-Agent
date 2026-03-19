# Backend (FastAPI)

Python backend for the Autonomous Research Agent.

## Run

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8001
```

## Endpoints

- `GET /health`
- `POST /api/research/run` with body:

```json
{
  "query": "Research the impact of AI on software engineering jobs from 2023 to 2026."
}
```

- `GET /api/research/stream?query=...` (SSE live progress + incremental `plan`/`source` events + final result)
- `POST /api/research/pdf` with body:

```json
{
  "title": "ARA Research Report",
  "markdown_text": "# Report\n\n..."
}
```
