#!/usr/bin/env bash
# Lane hash-relation gates on vy-hash-relation (RTX 4090): pytest (ligero + verity), the hashed gates of the three chain
# relations (honest >= 2048 VUs in l=16384 sub-batches + the committed-operand negatives + the relations' own families),
# and the bare gates (unchanged path) for the record.  Runs from the shipped tree (research run --source .).
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
SRC=$(pwd)
PY=/workspace/venv312/bin/python
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC"
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
fail=0
stage "tree"; cat "$SRC/.research-source.json" 2>/dev/null || true; nvidia-smi --query-gpu=name,memory.used --format=csv,noheader

if [ "${SKIP_PYTEST:-0}" != "1" ]; then
stage "pytest backends/direct/ligero (incl. hashchain_test, witness_device_test) + packages/verity/tests/commitments"
OMP_NUM_THREADS=16 "$PY" -m pytest backends/direct/ligero packages/verity/tests/commitments -q -x 2>&1 | tail -6
[ ${PIPESTATUS[0]} -eq 0 ] || fail=1
fi

for rel in fp8-ada bf16-hopper fp8-hopper; do
  stage "hashed gate $rel (cuda, 2048 honest VUs, l=16384)"
  "$PY" -m backends.direct.ligero.run --relation $rel gate-vu --device cuda --vus 2048 --batch 16384 --mode fiat-shamir \
      --auth included-hash --instances-cache /workspace/instances-cache --instance-procs 16 2>&1 | grep -v "REJECTED" | tail -12
  [ ${PIPESTATUS[0]} -eq 0 ] || fail=1
done

stage "hashed gate fp8-ada --zk interactive (cuda, 64 VUs)"
"$PY" -m backends.direct.ligero.run --relation fp8-ada gate-vu --device cuda --vus 64 --batch 4096 --mode interactive --zk \
    --auth included-hash --instances-cache /workspace/instances-cache 2>&1 | grep -v "REJECTED" | tail -6
[ ${PIPESTATUS[0]} -eq 0 ] || fail=1

stage "hashed gate fp8-ada tile 64x64 (cuda)"
"$PY" -m backends.direct.ligero.run --relation fp8-ada gate-vu --device cuda --vus 512 --batch 16384 --mode fiat-shamir \
    --auth included-hash --tile 64x64 --instances-cache /workspace/instances-cache --instance-procs 16 2>&1 | grep -v "REJECTED" | tail -8
[ ${PIPESTATUS[0]} -eq 0 ] || fail=1

stage "bare gate fp8-ada (unchanged path, cuda, 64 VUs)"
"$PY" -m backends.direct.ligero.run --relation fp8-ada gate-vu --device cuda --vus 64 --batch 4096 --mode fiat-shamir \
    --instances-cache /workspace/instances-cache 2>&1 | tail -3
[ ${PIPESTATUS[0]} -eq 0 ] || fail=1

stage "done"
if [ $fail -eq 0 ]; then echo GATES_OK; else echo GATES_FAILED; exit 1; fi
