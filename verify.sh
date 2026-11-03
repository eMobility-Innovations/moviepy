#!/usr/bin/env bash
# Execute only as a shared-runner payload; submission belongs in pre-push.
set -euo pipefail
cd "$(dirname "$0")"
if [[ "${CLAUDE_GATE_REMOTE:-}" != 0 ]]; then
  echo "Submit this script through claude-gate-run; local suite execution is refused." >&2
  exit 2
fi
command -v uv >/dev/null || { echo "Runner requires uv and Python 3.12." >&2; exit 2; }
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
export TMPDIR="$work/tmp"
mkdir -p "$TMPDIR"
# A new environment and empty package cache prove a cold normal-resolver install.
export UV_CACHE_DIR="$work/cache"
uv venv --python 3.12 "$work/venv"
python="$work/venv/bin/python"
# Keep upstream setuptools, metadata and declared test/doc extras unchanged.
# xdist 2.x supports upstream pytest<7; modern xdist requires newer pytest.
uv pip install --python "$python" '.[test,doc]' 'pytest-xdist<3'
uv pip check --python "$python"
"$python" -m pytest -n 1 --doctest-glob 'moviepy/**/**.py'   --cov moviepy --cov-report term-missing --cov-fail-under=80 -ra
