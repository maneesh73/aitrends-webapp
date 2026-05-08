#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== AI Pulse - Starting ==="

# nginx (www-data) needs execute on home dir to traverse to frontend/dist
chmod o+x "$HOME"

# Backend
cd "$SCRIPT_DIR/backend"
if [ ! -d ".venv" ]; then
  ~/.local/bin/uv venv .venv
  ~/.local/bin/uv pip install -r requirements.txt --python .venv
fi
cp --update=none .env.example .env 2>/dev/null || true
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "✓ Backend running  → http://localhost:8000  (API docs: /docs)"

# Node / fnm
export PATH="$HOME/.local/share/fnm:$PATH"
eval "$(fnm env 2>/dev/null)" || true

# Frontend
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
  npm install --silent
fi
npm run dev &
FRONTEND_PID=$!
echo "✓ Frontend running → http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
