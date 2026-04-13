#!/usr/bin/env bash
# Quant for Donkey — create venv and install dependencies (macOS / Linux).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  echo "Creating virtual environment in .venv ..."
  python3 -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Done."
echo "  Activate:  source .venv/bin/activate"
echo "  Dashboard: streamlit run dashboard.py"
echo "  CLI demo:  python main.py"
echo "  Tests:     pip install -r requirements-dev.txt && pytest tests -q"
