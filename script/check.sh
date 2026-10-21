#!/usr/bin/env bash
# Full gate: tests and lint. Run before every commit.
set -euo pipefail
cd "$(dirname "$0")/.."
bin=.venv/bin
[ -x "$bin/ruff" ] || bin=$(dirname "$(command -v ruff)")

"$bin/python" -m unittest -q "$@"
"$bin/ruff" check .
