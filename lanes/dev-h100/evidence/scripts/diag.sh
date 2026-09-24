#!/usr/bin/env bash
# diag.sh: separate network from GPU: bf16-hopper bare, --reps 1, batch 16384, pipeline 1 and 4, LOCAL coins (no --verifier), + GPU clocks/throttle.
set -uo pipefail
PY=/workspace/venv312/bin/python
export PYTHONPATH="$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/tools/research/src:$PWD"
RD=${RESEARCH_RUN_DIR:-/tmp}
nvidia-smi --query-gpu=clocks.sm,clocks.max.sm,clocks.mem,power.draw,power.limit,temperature.gpu,clocks_throttle_reasons.active,utilization.gpu,memory.used --format=csv
nvidia-smi --query-compute-apps=pid,used_memory --format=csv
for p in 1 4; do
  out="$RD/local_b16384_p$p.json"
  "$PY" -m backends.direct.ligero.run --relation bf16-hopper bench-vu --zk --mode interactive --target -128 --total-vus 4096 --reps 1 --batch 16384 --pipeline $p \
     --device cuda --instance-procs 16 --instances-cache /workspace/instances-cache --out "$out" > "$RD/local_b16384_p$p.log" 2>&1
  echo "rc=$?"; "$PY" - "$out" <<'PYEOF'
import json,sys
r=json.load(open(sys.argv[1])); md={e["name"]:e["value"] for e in r["measurements"]}
print(sys.argv[1].split("/")[-1], {k:round(v,3) for k,v in md.items() if isinstance(v,(int,float)) and (k.startswith("t.") or k.startswith("split."))})
PYEOF
done
nvidia-smi --query-gpu=clocks.sm,clocks.mem,power.draw,temperature.gpu,clocks_throttle_reasons.active --format=csv,noheader
