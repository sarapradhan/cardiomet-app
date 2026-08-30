#!/usr/bin/env bash
# scripts/deploy_hf_space.sh — publish the static frontend to a Hugging Face
# Static Space, pointed at a separately hosted API (e.g. Render).
#
# Why a *separate* build step rather than reusing frontend/out from the
# single-container Docker build: that build always bakes NEXT_PUBLIC_API_URL="",
# which only works when the UI and API share an origin (the Docker container).
# A Static Space has no backend of its own, so the UI needs a *different*
# build with NEXT_PUBLIC_API_URL pointed at the real API host — hence a
# dedicated build here rather than copying frontend/out as-is.
#
# Usage:
#   HF_SPACE=your-hf-username/your-space-name \
#   API_URL=https://your-api.onrender.com \
#   bash scripts/deploy_hf_space.sh
#
# Requires: the API host's ALLOWED_ORIGINS env var must include this Space's
# origin (https://<hf-username>-<space-name>.hf.space) or the deployed UI's
# requests will be blocked by CORS. See docs/DEPLOYMENT.md.
#
# Auth: git will prompt for HTTPS credentials on push. Username can be
# anything; password must be a Hugging Face access token with write access
# to the Space (huggingface.co -> Settings -> Access Tokens).
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."

: "${HF_SPACE:?Set HF_SPACE=your-hf-username/your-space-name}"
: "${API_URL:?Set API_URL=https://your-api-host (no trailing slash)}"

if [[ "$API_URL" == */ ]]; then
  echo "API_URL should not have a trailing slash (got: $API_URL)" >&2
  exit 1
fi

echo "Building frontend statically, NEXT_PUBLIC_API_URL=$API_URL ..."
if [[ ! -d frontend/node_modules ]]; then
  (cd frontend && npm install)
fi
(cd frontend && rm -rf .next out && NEXT_PUBLIC_API_URL="$API_URL" npm run build)

if [[ ! -f frontend/out/index.html ]]; then
  echo "Build did not produce frontend/out/index.html — aborting before touching the Space." >&2
  exit 1
fi

PUBLISH_DIR="$(mktemp -d)"
trap 'rm -rf "$PUBLISH_DIR"' EXIT

cp -r frontend/out/. "$PUBLISH_DIR/"

# Hugging Face Static Spaces read this frontmatter to know how to serve the
# repo. Without it (or with the wrong sdk), the Space fails to build.
cat > "$PUBLISH_DIR/README.md" << EOF
---
title: CardioMet Lens
emoji: 🫀
colorFrom: blue
colorTo: green
sdk: static
pinned: false
---

CardioMet Lens — educational cardiometabolic benchmarking. Static UI only;
calls a separately hosted API at build-configured NEXT_PUBLIC_API_URL.
Source and full docs: https://github.com/sarapradhan/cardiomet-app
EOF

cd "$PUBLISH_DIR"
git init -q
git checkout -q -b main
git add -A
git -c user.email="deploy@local" -c user.name="deploy script" commit -q -m "Deploy static export (API_URL=$API_URL)"

echo
echo "About to force-push the built static export to:"
echo "  https://huggingface.co/spaces/$HF_SPACE"
echo "This overwrites whatever is currently in that Space."

# Interactive (local) run: confirm first. Non-interactive run (CI, or any
# caller with no TTY on stdin): skip the prompt - there's nothing to read it,
# and a stuck `read` would just hang the job until it times out.
if [[ -t 0 ]]; then
  read -r -p "Continue? [y/N] " confirm
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted — nothing was pushed."
    exit 1
  fi
fi

# With HF_TOKEN set (CI, or a local export), authenticate the push directly
# in the remote URL - HF ignores the username for token auth, so any
# placeholder works. Without it, git falls back to an interactive credential
# prompt (local use: paste an access token as the password when asked).
if [[ -n "${HF_TOKEN:-}" ]]; then
  git remote add space "https://user:${HF_TOKEN}@huggingface.co/spaces/$HF_SPACE"
else
  git remote add space "https://huggingface.co/spaces/$HF_SPACE"
fi
git push --force space main

echo
echo "Deployed. Visit: https://huggingface.co/spaces/$HF_SPACE"
echo "Reminder: confirm ALLOWED_ORIGINS on $API_URL includes this Space's origin."
