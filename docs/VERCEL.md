# Vercel Deployment

This repository is configured to deploy the React/Vite dashboard to Vercel from the repository root.

The FastAPI backend uses PostgreSQL, Redis, Celery, long-running workers, and websocket behavior. Deploy it on a backend platform that supports those services, then point Vercel to that backend with environment variables.

## Vercel project settings

Use these settings if connecting the GitHub repository in Vercel:

- Framework preset: `Vite`
- Root directory: repository root
- Install command: `cd frontend && npm ci`
- Build command: `cd frontend && npm run build`
- Output directory: `frontend/dist`

The same values are already captured in `vercel.json`.

## Required Vercel environment variables

Set these in Vercel Project Settings -> Environment Variables:

```text
VITE_API_URL=https://your-backend.example.com/api/v1
VITE_WS_URL=wss://your-backend.example.com/api/v1/ws
```

Examples:

- If the backend is hosted at `https://algo-api.example.com`, use:
  - `VITE_API_URL=https://algo-api.example.com/api/v1`
  - `VITE_WS_URL=wss://algo-api.example.com/api/v1/ws`
- For local frontend development against Docker backend:
  - `VITE_API_URL=http://localhost:8000/api/v1`
  - `VITE_WS_URL=ws://localhost:8000/api/v1/ws`

## Deploy with Vercel CLI

```bash
export VERCEL_TOKEN=your-token
./scripts/deploy-vercel.sh
```

Or manually:

```bash
npx vercel deploy --prod --token "$VERCEL_TOKEN"
```

## Backend deployment note

Vercel is not the right target for the full backend in its current production architecture because the backend requires:

- persistent PostgreSQL
- Redis
- Celery workers
- long-running broker/feed processes
- websocket connections

Use Docker Compose on a VM, Railway, Render, Fly.io, ECS, Kubernetes, or another platform that supports long-running containers and managed Postgres/Redis.
