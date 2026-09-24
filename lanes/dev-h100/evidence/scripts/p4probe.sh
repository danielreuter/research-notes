#!/usr/bin/env bash
# p4probe.sh: characterise the bf16-hopper pipelined completeness failure (LOCAL coins, interactive ZK, --reps 3, no dumps): p3/16384, p4/16384 again, p4/8192, p4/32768.
set -uo pipefail
PY=/workspace/venv312/bin/python
export PYTHONPATH="$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/tools/research/src:$PWD"
RD=${RESEARCH_RUN_DIR:-/tmp}
for cfg in "16384 3" "16384 4" "8192 4" "32768 4" "16384 2"; do
  set -- $cfg; b=$1; p=$2
  echo "=== [$(date -u +%H:%M:%S)] bf16-hopper --batch $b --pipeline $p --reps 3 (local coins)"
  "$PY" -m backends.direct.ligero.run --relation bf16-hopper bench-vu --zk --mode interactive --target -128 --total-vus 4096 --reps 3 --batch $b --pipeline $p \
     --device cuda --instance-procs 16 --instances-cache /workspace/instances-cache --out "$RD/probe_b${b}_p${p}.json" > "$RD/probe_b${b}_p${p}.log" 2>&1
  rc=$?; echo "PROBE batch=$b pipeline=$p rc=$rc"; grep -h "^rep \|AssertionError" "$RD/probe_b${b}_p${p}.log" | cut -c1-160
done
