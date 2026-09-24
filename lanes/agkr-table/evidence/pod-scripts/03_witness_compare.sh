#!/usr/bin/env bash
# agkr-table: the device witness generator (gpu/v2/witness.py) vs the CPU export of vu-k1536 [0, 4096) (units.bin,
# epilogue.bin, public.bin byte for byte), 3 timed reps.
set -uo pipefail
source /workspace/env.sh
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
echo "=== $(date -u +%H:%M:%S) compare"
$PY -m gpu.v2.witness compare /workspace/agkr-table/bb/pos4096 --root /workspace/bench-instances/v1 --tier vu-k1536 --reps 3
echo "rc=$? $(date -u +%H:%M:%S)"
