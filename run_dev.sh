#!/usr/bin/env sh
set -e

API_CMD="python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
FRONTEND_CMD="cd frontend && npm run dev"

cleanup() {
  echo "Stopping services..."
  kill "$(jobs -p)" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

printf "Starting API on http://localhost:8000\n"
printf "Starting Next.js frontend on http://localhost:3000\n\n"

sh -c "$API_CMD" &
sh -c "$FRONTEND_CMD" &

wait
