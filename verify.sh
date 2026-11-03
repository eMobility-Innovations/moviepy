#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
# Upstream stable CI declares Python 3.9–3.11; exercise its highest declared target.
work_dir="$(mktemp -d "${TMPDIR:-/tmp}/moviepy-gate.XXXXXX")"
trap 'rm -rf "$work_dir"' EXIT
uv venv --python 3.11 "$work_dir/venv"
uv pip install --python "$work_dir/venv/bin/python" ".[test]" "pillow>=13,<14" pytest-xdist
uv pip check --python "$work_dir/venv/bin/python"
# Eight pytest workers share the job's existing 2 GiB ceiling. Prevent each
# BLAS/FFmpeg child from creating a machine-wide thread pool of its own.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export MOVIEPY_GATE_REAL_FFMPEG
MOVIEPY_GATE_REAL_FFMPEG="$("$work_dir/venv/bin/python" -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')"
cat > "$work_dir/ffmpeg" <<'FFMPEG'
#!/usr/bin/env bash
set -euo pipefail
args=("$@")
writer=0
explicit_threads=0
for arg in "${args[@]}"; do
    if [[ "$arg" == "-y" ]]; then writer=1; fi
    if [[ "$arg" == "-threads" ]]; then explicit_threads=1; fi
done
if [[ "$writer" == 1 && "$explicit_threads" == 0 ]]; then
    count="${#args[@]}"
    exec "$MOVIEPY_GATE_REAL_FFMPEG" -cpucount 1 -threads 1 \
        "${args[@]:0:count-1}" -threads 1 "${args[count-1]}"
fi
exec "$MOVIEPY_GATE_REAL_FFMPEG" -cpucount 1 -threads 1 "${args[@]}"
FFMPEG
chmod +x "$work_dir/ffmpeg"
# FFmpeg documents -cpucount as a test-only CPU detection override:
# https://ffmpeg.org/ffmpeg.html#Generic-options
export FFMPEG_BINARY="$work_dir/ffmpeg" IMAGEIO_FFMPEG_EXE="$work_dir/ffmpeg"
workers="$("$work_dir/venv/bin/python" -c 'import tomllib; print(tomllib.load(open("REPO-CONTRACT.toml", "rb"))["tests"]["parallel"])')"
"$work_dir/venv/bin/python" -m pytest -n "$workers" tests/test_pillow13_compat.py -q
"$work_dir/venv/bin/python" tests/prove_pillow13_guard.py "$workers"
"$work_dir/venv/bin/python" -m pytest -n "$workers" tests/ -v -x --tb=short --durations=20 --cov=moviepy --cov-report=term-missing --cov-fail-under=80
