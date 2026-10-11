#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p models .runtime data
if [[ ! -x .venv/bin/python ]]; then
  if command -v uv >/dev/null; then uv venv --python 3.12 .venv
  else python3 -m venv .venv
  fi
fi
if command -v uv >/dev/null; then uv pip install --python .venv/bin/python -r requirements.txt
else .venv/bin/python -m pip install -r requirements.txt
fi
mkdir -p models/kokoro
VOICE_BASE=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1
for file in kokoro-v1.0.onnx voices-v1.0.bin; do
  if [[ ! -f "models/kokoro/$file" ]]; then
    curl -4 -fL --retry 3 "$VOICE_BASE/$file" -o "models/kokoro/$file.download"
    mv "models/kokoro/$file.download" "models/kokoro/$file"
  fi
done
if ! command -v ollama >/dev/null && [[ ! -x .runtime/ollama ]]; then
  if [[ "$(uname -s)" == Darwin ]]; then
    curl -4 -fL --retry 3 https://ollama.com/download/ollama-darwin.tgz -o .runtime/ollama.tgz
    tar -xzf .runtime/ollama.tgz -C .runtime
    rm .runtime/ollama.tgz
  else
    echo 'Install Ollama from https://ollama.com/download, then rerun setup.' >&2
    exit 1
  fi
fi
export OLLAMA_MODELS="$PWD/models/ollama"
export OLLAMA_NO_CLOUD=1
# CPU mode is reliable in constrained desktop environments; override for GPU use.
export LLAMA_ARG_DEVICE="${LLAMA_ARG_DEVICE:-none}"
export LLAMA_ARG_KV_OFFLOAD="${LLAMA_ARG_KV_OFFLOAD:-0}"
export OLLAMA_LLM_LIBRARY="${OLLAMA_LLM_LIBRARY:-cpu}"
export OLLAMA_HOST=127.0.0.1:11434
OLLAMA_BIN="$(command -v ollama || true)"
if [[ -z "$OLLAMA_BIN" ]]; then OLLAMA_BIN="$PWD/.runtime/ollama"; fi
if ! curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null; then
  "$OLLAMA_BIN" serve >data/ollama.log 2>&1 &
  OLLAMA_CHILD=$!
  trap 'kill "$OLLAMA_CHILD" 2>/dev/null || true' EXIT
  for attempt in {1..30}; do
    if curl -fsS --max-time 1 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then break; fi
    sleep 1
  done
fi
if ! "$OLLAMA_BIN" pull "${WANDERLORE_MODEL:-gemma3:1b}"; then
  if [[ "${WANDERLORE_MODEL:-gemma3:1b}" == "gemma3:1b" ]]; then
    .venv/bin/python scripts/download_model.py
  else exit 1
  fi
fi
echo 'Ready. Start Wanderlore with ./scripts/run.sh'
