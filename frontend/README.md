# Frontend (Next.js)

Native Next.js App Router frontend for ARA.

## Run on Port 3001

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Configure API base URL:

```bash
cp .env.local.example .env.local
```

3. Start dev server:

```bash
npm run dev
```

4. Open:

- `http://localhost:3001`

## UI Notes

- Clean, minimal layout
- Dark/light theme toggle
- Next.js icon shown in the header
- App icon set to `public/icon.svg`
- Live progress timeline over SSE while backend nodes execute
- Plan items render immediately after planner step completes
- Sources render incrementally one-by-one as stream events arrive
- Connected to backend endpoints:
  - `GET /api/research/stream?query=...`
  - `POST /api/research/pdf`
