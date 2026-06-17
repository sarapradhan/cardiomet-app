#!/usr/bin/env bash
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
G='\033[0;32m'; R='\033[0;31m'; E='\033[0m'

echo "SAHC RiskLens — Environment Setup"
echo ""

python3 -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)" || \
  { echo -e "${R}✗ Python 3.11+ required${E}"; exit 1; }
echo -e "${G}  ✓ Python $(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')${E}"

[[ -d ".venv" ]] || python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q && pip install -r requirements.txt -q
echo -e "${G}  ✓ Python dependencies installed${E}"

command -v node &>/dev/null && node -e "process.exit(parseInt(process.version.slice(1))>=18?0:1)" || \
  { echo -e "${R}✗ Node.js 18+ required — https://nodejs.org${E}"; exit 1; }
echo -e "${G}  ✓ Node.js $(node --version)${E}"

[[ -f "frontend/package.json" ]] && { (cd frontend && npm install -s); echo -e "${G}  ✓ Frontend deps installed${E}"; }

[[ -f ".env" ]]              || { cp .env.example .env; echo "  Created .env"; }
[[ -f "frontend/.env.local" ]] || [[ ! -f "frontend/.env.local.example" ]] || \
  { cp frontend/.env.local.example frontend/.env.local; echo "  Created frontend/.env.local"; }

echo ""
echo "Setup complete."
echo "  source .venv/bin/activate"
echo "  python scripts/download_nhanes.py"
echo "  # T1: uvicorn api.main:app --reload"
echo "  # T2: cd frontend && npm run dev"
