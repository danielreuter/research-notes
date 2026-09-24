#!/usr/bin/env bash
# Lane merge-val: items (a)-(g) on vy-merge-val from the synced merged tree /workspace/src (main a55b3fc).
# Every command + exit code is appended to /workspace/mv/commands.log; each item's full output in /workspace/mv/<item>.log.
# Usage: items.sh <item> [<item> ...]   (items: a b c d e f g rust_e rust_f rust_g)
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
SRC=/workspace/src
PY=/workspace/venv312/bin/python
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC"
export OMP_NUM_THREADS=16
LOG=/workspace/mv/commands.log
RV="$SRC/backends/ligero-verify/target/release/ligero-verify"
CACHE="--instance-procs 8 --instances-cache /workspace/instances-cache"
LIVE="tcp://213.173.105.69:30899"
cd "$SRC"
mkdir -p /workspace/mv /tmp/mv
run() {  # item, then the command
  local item=$1; shift
  local t0; t0=$(date -u +%s)
  echo "[$(date -u +%H:%M:%SZ)] ($item) START: $*" | tee -a "$LOG"
  "$@" > "/workspace/mv/$item.log" 2>&1
  local rc=$?
  echo "[$(date -u +%H:%M:%SZ)] ($item) EXIT=$rc  elapsed=$(( $(date -u +%s) - t0 ))s" | tee -a "$LOG"
  return $rc
}
BENCH_E="--relation fp8-ada bench-vu --zk --mode interactive --batch 16384 --total-vus 1024 --reps 1 --target -128 --device cuda"
for item in "$@"; do
case "$item" in
  a) run a "$PY" -m pytest -q backends/direct/ligero -x -p no:cacheprovider ;;
  b) run b1 "$PY" -m backends.direct.ligero.run --relation fp8-ada gate-vu --device cuda --vus 2048 --batch 4096 $CACHE
     run b2 "$PY" -m backends.direct.ligero.run --relation bf16-hopper gate-vu --device cuda --vus 2048 --batch 4096 $CACHE ;;
  c) run c "$PY" -m backends.direct.ligero.run --relation fp8-ada gate-vu --device cuda --vus 2048 --batch 16384 --auth included-hash $CACHE ;;
  d) run d "$PY" -m backends.direct.ligero.run --relation fp8-ada-v3 gate-vu --device cuda --vus 2048 --batch 4096 $CACHE ;;
  e) run e "$PY" -m backends.direct.ligero.run $BENCH_E --pipeline 2 --verifier $LIVE $CACHE \
        --out /tmp/mv/bare/result.json --dump-dir /tmp/mv/bare/proofs --dump-reps 1 ;;
  f) run f "$PY" -m backends.direct.ligero.run $BENCH_E --auth included-hash --verifier $LIVE $CACHE \
        --out /tmp/mv/hash/result.json --dump-dir /tmp/mv/hash/proofs --dump-reps 1 ;;
  f2) run f2 "$PY" -m backends.direct.ligero.run $BENCH_E --auth included-hash $CACHE \
        --out /tmp/mv/hash2/result.json --dump-dir /tmp/mv/hash2/proofs --dump-reps 1 ;;
  g) run g "$PY" -m backends.direct.ligero.run $BENCH_E --pipeline 2 $CACHE \
        --out /tmp/mv/local/result.json --dump-dir /tmp/mv/local/proofs --dump-reps 1 ;;
  e1) run e1 "$PY" -m backends.direct.ligero.run $BENCH_E --pipeline 1 --verifier $LIVE $CACHE \
        --out /tmp/mv/bare1/result.json --dump-dir /tmp/mv/bare1/proofs --dump-reps 1 ;;
  g1) run g1 "$PY" -m backends.direct.ligero.run $BENCH_E --pipeline 1 $CACHE \
        --out /tmp/mv/local1/result.json --dump-dir /tmp/mv/local1/proofs --dump-reps 1 ;;
  g_nozk) run g_nozk "$PY" -m backends.direct.ligero.run --relation fp8-ada bench-vu --mode interactive --batch 16384 --total-vus 1024 --reps 1 --target -128 --device cuda --pipeline 2 $CACHE \
        --out /tmp/mv/local_nozk/result.json --dump-dir /tmp/mv/local_nozk/proofs --dump-reps 1 ;;
  rust_e1) run rust_e1 "$RV" batch --dir /tmp/mv/bare1/proofs/rep1 --system /tmp/mv/bare1/proofs/system.bin --target-bits 128 ;;
  rust_g1) run rust_g1 "$RV" batch --dir /tmp/mv/local1/proofs/rep1 --system /tmp/mv/local1/proofs/system.bin --target-bits 128 ;;
  rust_g_nozk) run rust_g_nozk "$RV" batch --dir /tmp/mv/local_nozk/proofs/rep1 --system /tmp/mv/local_nozk/proofs/system.bin --target-bits 128 ;;
  rust_e) run rust_e "$RV" batch --dir /tmp/mv/bare/proofs/rep1 --system /tmp/mv/bare/proofs/system.bin --target-bits 128 ;;
  rust_f) run rust_f "$RV" batch --dir /tmp/mv/hash/proofs/rep1 --system /tmp/mv/hash/proofs/system.bin --target-bits 128 ;;
  rust_f2) run rust_f2 "$RV" batch --dir /tmp/mv/hash2/proofs/rep1 --system /tmp/mv/hash2/proofs/system.bin --target-bits 128 ;;
  rust_g) run rust_g "$RV" batch --dir /tmp/mv/local/proofs/rep1 --system /tmp/mv/local/proofs/system.bin --target-bits 128 ;;
  *) echo "unknown item $item" ;;
esac
done
