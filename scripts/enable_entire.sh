#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -z "${ENTIRE_BIN:-}" ]]; then
  if [[ -x "$PWD/.runtime/entire-cli/entire" ]]; then ENTIRE_BIN="$PWD/.runtime/entire-cli/entire"
  else ENTIRE_BIN=entire; fi
fi
if ! command -v "$ENTIRE_BIN" >/dev/null; then
  echo 'Install Entire from https://github.com/entireio/cli, then rerun this script.' >&2
  exit 1
fi
# Records future supported Codex sessions locally. Does not publish or backfill.
"$ENTIRE_BIN" enable --agent codex --telemetry=false --skip-push-sessions --skip-initial-commit --no-init-repo --absolute-git-hook-path --local
"$ENTIRE_BIN" status
