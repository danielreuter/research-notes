#!/usr/bin/env bash
# instance-equiv/v1 documents for the two +sha256 x4 cells (PR #21 shape): candidate = relchain.instances_ref(<rel>, n),
# frozen = the target's declared set over [0, n).  Then --check re-derives each from its candidate ref.
#   research run --on vy-reverify-fp4 --project verity --custody-r2 --cwd /workspace/src -- bash <this>
set -euo pipefail
source /workspace/env.sh
out=${RESEARCH_RUN_DIR:-/workspace/reverify-fp4}/outputs
mkdir -p "$out"
$PY -m verity_numerical.bench.instance_equiv --relation fp8-hopper-x4 --vus 32768 --procs "$VY_CPU_THREADS" --out "$out/instance-equiv-fp8-hopper-x4-32768.json"
$PY -m verity_numerical.bench.instance_equiv --relation bf16-hopper-x4 --vus 8192 --procs "$VY_CPU_THREADS" --out "$out/instance-equiv-bf16-hopper-x4-8192.json"
$PY -m verity_numerical.bench.instance_equiv --check "$out"/instance-equiv-*.json
