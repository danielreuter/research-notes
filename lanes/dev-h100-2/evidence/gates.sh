#!/usr/bin/env bash
# Gates (brief §2) on vy-dev-h100-2 from the post-freeze tree 11c7075 (cwd = the shipped tree): bf16-hopper / fp8-hopper bare + included-hash.
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
PY=/workspace/venv312/bin/python
export LIGERO_VERIFY=/workspace/bin/ligero-verify
export OMP_NUM_THREADS=16 TORCH_NUM_THREADS=16 MKL_NUM_THREADS=16
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
fails=0
for rel in bf16-hopper fp8-hopper; do
  for auth in "" "--auth included-hash"; do
    stage "gate: --relation $rel gate-vu --vus 2048 --batch 16384 $auth"
    t0=$(date +%s)
    "$PY" -m backends.direct.ligero.run --relation $rel gate-vu --vus 2048 --batch 16384 --device cuda --target -128 --instance-procs 16 --instances-cache /workspace/instances-cache $auth 2>&1 | tail -30
    rc=${PIPESTATUS[0]}; echo "gate rc=$rc wall=$(( $(date +%s) - t0 ))s  [$rel $auth]"
    [ "$rc" -eq 0 ] || fails=$((fails+1))
  done
done
stage "GATES_DONE fails=$fails"
[ "$fails" -eq 0 ]
