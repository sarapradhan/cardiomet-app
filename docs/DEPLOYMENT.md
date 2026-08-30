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

**Railway / Fly.io / a Hugging Face Space (Docker SDK):** same idea — point it
at the repo, it builds the Dockerfile, one URL. No env vars are required for
demo mode. Requires Docker-enabled Spaces access on Hugging Face — see below
if that's not available on your account.

**Notes**
- Demo mode needs no data files (the NHANES percentiles are baked in). To run the
  live-data path, uncomment the `COPY data/raw/` line in the Dockerfile and add
  the files, or download them in a build step.
- Because UI and API share an origin, no CORS config or `NEXT_PUBLIC_API_URL` is
  needed in the container.
- The image is built multi-stage (Node builds the static UI, Python serves it),
  so the final image carries only the Python runtime + built assets.

## Split deployment: Static Space (Hugging Face) + API elsewhere

If Docker isn't available on your Hugging Face account, the app splits
cleanly into two independent free hosts instead of one container: a
**Static Space** serves the already-static Next.js export (`frontend/out`),
and a separate host runs the API. The UI calls the API over HTTPS instead of
same-origin, so this needs two things the single-container path doesn't:

1. **API host with CORS configured.** Deploy the API-only side the same way
   as the Render option above (the container still runs the FastAPI app; the
   embedded static files it also serves just go unused). Set the
   `ALLOWED_ORIGINS` env var on that host to include the Space's origin,
   e.g. `ALLOWED_ORIGINS=https://<hf-username>-<space-name>.hf.space`
   (`api/main.py` already reads this — no code change needed).
2. **Static Space built against that API URL.** Next.js bakes
   `NEXT_PUBLIC_API_URL` in at *build* time (static export has no server to
   read env vars at runtime), so the Space's build must happen with the
   API's real URL, not the empty string the Docker build uses.

**One-time setup:**
1. Create a Space on huggingface.co with SDK = **Static**.
2. Deploy the API (Render, Railway, Fly.io — same steps as above, Docker SDK
   *not* required here since none of those hosts need HF's Docker access).
3. Set `ALLOWED_ORIGINS` on that API host to the Space's URL.

**To publish (manual, run anytime):**
```bash
HF_SPACE=your-hf-username/your-space-name \
API_URL=https://your-api-host.onrender.com \
bash scripts/deploy_hf_space.sh
```
Builds the frontend with that API URL baked in, then force-pushes the static
output (plus a generated Space README with the required `sdk: static`
frontmatter) to the Space's git repo. Prompts for confirmation before
pushing; git will then prompt for HTTPS credentials — username can be
anything, password must be a Hugging Face access token with write access to
the Space (huggingface.co → Settings → Access Tokens).

**To automate on every merge to `main`:** add three repo secrets
(`HF_TOKEN`, `HF_SPACE`, `RENDER_API_URL`) under Settings → Secrets and
variables → Actions. `.github/workflows/deploy-hf-space.yml` then publishes
automatically after CI passes. Without those secrets it skips cleanly with a
warning in the run summary — it never silently no-ops.
