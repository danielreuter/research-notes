#!/usr/bin/env bash
# agkr-bound: negatives of the operands-committed scaffold with the root pins compiled in (commitments.rs PINS)
# research run --on vy-agkr-bound2 --project verity --source . --cwd source/backends/gkr --send 11_commit_neg.sh --send 10_commit_neg.py \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/11_commit_neg.sh" [cells]'
#  0. cargo build --release + cargo test --release -> /workspace/bin/verity-gkr-verify-pinned
#  1. per cell: 10_commit_neg.py against the circuit export 09 left at /workspace/agkr-bound/commit/<rel>-<leaf>/stmt
# usage: bash 11_commit_neg.sh [cells...]   cell = <relation>:<sha256|blake3>
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT/tools/research/src:$ROOT:$HERE"
export CARGO_TARGET_DIR=/workspace/cargo-target PATH="/workspace/venv312/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/workspace/venv312/bin/python
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT CARGO_BUILD_JOBS=$NT
RD=${RESEARCH_RUN_DIR:?}
echo "tree $ROOT; commit ${RESEARCH_SOURCE_COMMIT:-?}; cpu threads $NT; run dir $RD"
H=/workspace/agkr-bound/commit
CELLS=${*:-bf16-ampere:sha256 fp8-hopper:blake3}

echo "== 0. verifier ($(date -u +%H:%M:%S))"
( cd verifier && cargo build --release 2>&1 | grep -E "^(warning|error)|Finished" | head -20 && cargo test --release 2>&1 | grep -E "^test result|FAILED|panicked|^error" )
VB=/workspace/bin/verity-gkr-verify-pinned
cp $CARGO_TARGET_DIR/release/verity-gkr-verify $VB && sha256sum $VB

for cell in $CELLS; do
  c=${cell%%:*}; l=${cell##*:}
  S=$H/$c-$l/stmt; O=$H/neg-$c-$l
  echo "== 1. negatives $c $l ($(date -u +%H:%M:%S))"
  [ -f $S/manifest.json ] || { echo "no export at $S"; continue; }
  rm -rf $O; mkdir -p $O
  $PY "$RD/inputs/10_commit_neg.py" $c $l $S $O $VB 4096 $NT > $O/neg.log 2>&1
  echo "neg rc=$? ($(date -u +%H:%M:%S))"
  tail -30 $O/neg.log | cut -c1-240
done
echo "== done ($(date -u +%H:%M:%S))"
