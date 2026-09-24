#!/usr/bin/env bash
# Lane dev-4090 gates (brief §2) on vy-dev-4090, frozen tree /workspace/src (64c00bd).
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
SRC=/workspace/src
PY=/workspace/venv312/bin/python
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
export OMP_NUM_THREADS=16
LOG=/workspace/d4090/commands.log
CACHE="--instance-procs 16 --instances-cache /workspace/instances-cache"
cd "$SRC"
mkdir -p /workspace/d4090
run() {  # item, then the command
  local item=$1; shift
  local t0; t0=$(date -u +%s)
  echo "[$(date -u +%H:%M:%SZ)] ($item) START: $*" | tee -a "$LOG"
  "$@" > "/workspace/d4090/$item.log" 2>&1
  local rc=$?
  echo "[$(date -u +%H:%M:%SZ)] ($item) EXIT=$rc  elapsed=$(( $(date -u +%s) - t0 ))s" | tee -a "$LOG"
  return $rc
}
for item in "$@"; do
case "$item" in
  pytest) run pytest "$PY" -m pytest backends/direct/ligero -q -x -p no:cacheprovider ;;
  gate_bare) run gate_bare "$PY" -m backends.direct.ligero.run --relation fp8-ada gate-vu --vus 2048 --batch 16384 --device cuda $CACHE ;;
  gate_hash) run gate_hash "$PY" -m backends.direct.ligero.run --relation fp8-ada gate-vu --vus 2048 --batch 16384 --device cuda --auth included-hash $CACHE ;;
  *) echo "unknown item $item" ;;
esac
done
