#!/usr/bin/env bash
# --check of 20-equiv.sh's two documents (run r20260925-164233-1830 outputs), each at its own n (20-equiv.sh's own --check
# ran at the default --vus 4096 and could not match the candidate refs).
#   research run --on vy-reverify-fp4 --project verity --custody-r2 --cwd /workspace/src -- bash <this>
set -euo pipefail
source /workspace/env.sh
d=/workspace/research/runs/r20260925-164233-1830/outputs
$PY -m verity_numerical.bench.instance_equiv --vus 32768 --procs "$VY_CPU_THREADS" --check "$d/instance-equiv-fp8-hopper-x4-32768.json"
$PY -m verity_numerical.bench.instance_equiv --vus 8192 --procs "$VY_CPU_THREADS" --check "$d/instance-equiv-bf16-hopper-x4-8192.json"
