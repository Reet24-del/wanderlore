#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OLLAMA_MODELS="$PWD/models/ollama"
export OLLAMA_NO_CLOUD=1
# CPU mode is reliable in constrained desktop environments; override for GPU use.
export LLAMA_ARG_DEVICE="${LLAMA_ARG_DEVICE:-none}"
export LLAMA_ARG_KV_OFFLOAD="${LLAMA_ARG_KV_OFFLOAD:-0}"
export OLLAMA_LLM_LIBRARY="${OLLAMA_LLM_LIBRARY:-cpu}"
export OLLAMA_HOST=127.0.0.1:11434
export OTEL_SDK_DISABLED=true
export HF_HUB_OFFLINE=1
export HF_HUB_DISABLE_TELEMETRY=1
if [[ ! -x .venv/bin/python ]]; then
  echo 'Run ./scripts/setup.sh once first.' >&2
  exit 1
fi
if ! curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null; then
  if [[ -x .runtime/ollama ]]; then
    mkdir -p data
    .runtime/ollama serve >data/ollama.log 2>&1 &
    OLLAMA_CHILD=$!
    trap 'kill "$OLLAMA_CHILD" 2>/dev/null || true' EXIT
    for attempt in {1..30}; do
      if curl -fsS --max-time 1 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then break; fi
      sleep 1
    done
  elif command -v ollama >/dev/null; then
    ollama serve >data/ollama.log 2>&1 &
    OLLAMA_CHILD=$!
    trap 'kill "$OLLAMA_CHILD" 2>/dev/null || true' EXIT
  fi
fi
HOST="${WANDERLORE_HOST:-127.0.0.1}"
PORT="${WANDERLORE_PORT:-8765}"
printf 'Wanderlore: http://%s:%s\n' "$HOST" "$PORT"
if [[ -f .env ]]; then set -- --env-file .env "$@"; fi
.venv/bin/python -m uvicorn app.main:app --host "$HOST" --port "$PORT" "$@"
