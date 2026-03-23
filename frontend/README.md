# Frontend Web App

Next.js App Router frontend for interacting with the Autonomous Research Agent backend in real time.

## What It Does

- Accepts natural-language research prompts
- Shows live pipeline progress while the backend streams execution events
- Renders plan steps and discovered sources incrementally
- Displays final generated report in the UI
- Supports light/dark mode with persisted theme preference

## Tech Stack

- Next.js 16
- React 18
- TypeScript
- CSS (custom design system)

## Prerequisites

- Node.js `18+` (or `20+` recommended)
- npm

## Environment

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
```

If unset, the app defaults to `http://localhost:8001`.

## Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Run in development mode:

```bash
npm run dev
```

3. Open:

- `http://localhost:3001`

## Docker

From project root:

```bash
docker compose up --build frontend
```

## Available Scripts

- `npm run dev` -> start dev server on port `3001`
- `npm run build` -> create production build
- `npm run start` -> run production server on port `3001`
- `npm run lint` -> run ESLint

## Backend Endpoints Used

- `GET /api/research/stream?query=...`
- `POST /api/research/pdf`

## Project Layout

```text
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   └── theme-toggle.tsx
├── package.json
└── README.md
```
