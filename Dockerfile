# ---- Stage 1: build the frontend static export ----
FROM node:20-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install
COPY frontend/ ./
# Same-origin: API is served from the same container, so base URL is empty.
ENV NEXT_PUBLIC_API_URL=""
RUN npm run build      # emits ./out (static export)

# ---- Stage 2: python API that also serves the static frontend ----
FROM python:3.12-slim AS app
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# App code
COPY sahc_risklens/ ./sahc_risklens/
COPY api/ ./api/
COPY cardiosafebench/ ./cardiosafebench/
COPY pyproject.toml ./
# Built frontend from stage 1
COPY --from=frontend /app/frontend/out ./frontend/out
# Optional: bundle NHANES data if present at build time (demo mode works without)
# COPY data/raw/ ./data/raw/
EXPOSE 8000
# Hosts set $PORT; default to 8000 locally.
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
