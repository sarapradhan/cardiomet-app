# Deployment — Single Container

SAHC RiskLens packages as one container that serves both the web UI and the API
from a single URL. This is the simplest path for both a shareable demo and a real
product.

## Run locally with Docker
```bash
docker compose up --build
# open http://localhost:8000
```
That's it — the UI is at `/`, the API at `/api/v1/...`, health at `/health`.

## Run locally without Docker (two terminals)
```bash
# terminal 1 — API
source .venv/bin/activate
uvicorn api.main:app --reload                       # http://localhost:8000
# terminal 2 — UI (dev mode, hot reload)
cd frontend && NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev   # http://localhost:3000
```

## Deploy to a host (free / low-cost options)
The container listens on `$PORT` (defaults to 8000), so it runs as-is on most hosts.

**Render (free web service):**
1. Push the repo to GitHub.
2. New → Web Service → connect the repo → Environment: Docker.
3. Deploy. Render sets `$PORT` automatically. You get one HTTPS URL.

**Railway / Fly.io / a Hugging Face Space (Docker):** same idea — point it at the
repo, it builds the Dockerfile, one URL. No env vars are required for demo mode.

**Notes**
- Demo mode needs no data files (the NHANES percentiles are baked in). To run the
  live-data path, uncomment the `COPY data/raw/` line in the Dockerfile and add
  the files, or download them in a build step.
- Because UI and API share an origin, no CORS config or `NEXT_PUBLIC_API_URL` is
  needed in the container.
- The image is built multi-stage (Node builds the static UI, Python serves it),
  so the final image carries only the Python runtime + built assets.
