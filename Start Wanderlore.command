#!/bin/bash
cd "$(dirname "$0")"
if curl -fsS --max-time 2 http://127.0.0.1:8766/api/health >/dev/null; then
  echo "Wanderlore is already running at http://127.0.0.1:8766"
  exit 0
fi
echo "Open http://127.0.0.1:8766 and keep this window open while using Wanderlore."
WANDERLORE_PORT=8766 ./scripts/run.sh
