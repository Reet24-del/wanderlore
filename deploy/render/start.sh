#!/usr/bin/env bash
set -euo pipefail
cd /app
python -m deploy.render.seed
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}" --no-proxy-headers
