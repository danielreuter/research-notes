#!/usr/bin/env bash
# Generate the four frozen instance sets (x, W, y per VU) as sp1-format-instances/v1 files, from the synced worktree.
# Usage on the pod: nohup bash gen_instances.sh [formats...] > /workspace/sp1-formats/gen.out 2>&1 &
set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.sp1/bin:$PATH"
SRC=${SRC:-/workspace/src}
W=/workspace/sp1-formats
OUT=$W/inst
VENV=$W/venv
mkdir -p "$OUT"
command -v uv >/dev/null || curl -fsSL https://astral.sh/uv/install.sh | sh >/dev/null
if [ ! -x "$VENV/bin/python" ]; then
  uv venv "$VENV" --python 3.12
  uv pip install --python "$VENV/bin/python" numpy torch --index-url https://download.pytorch.org/whl/cpu
fi
cd "$SRC"
export PYTHONPATH=$SRC/tools/research/src:$SRC/packages/verity/src:$SRC/backends/sp1/python:$SRC/backends/numerical/python
FORMATS=${*:-fp8-ada fp8-hopper bf16-hopper fp4-nvf4}
for f in $FORMATS; do
  echo "=== $(date -u +%H:%M:%S) $f"
  "$VENV/bin/python" -m verity_sp1.format_instances --format "$f" --n 4096 --procs "${PROCS:-12}" --out "$OUT/$f.bin"
done
sha256sum "$OUT"/*.bin
echo "=== done $(date -u +%H:%M:%S)"
