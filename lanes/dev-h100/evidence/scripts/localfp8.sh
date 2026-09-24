#!/usr/bin/env bash
PY=/workspace/venv312/bin/python
export PYTHONPATH="$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/tools/research/src:$PWD"
RD=${RESEARCH_RUN_DIR:-/tmp}
"$PY" -m backends.direct.ligero.run --relation fp8-hopper bench-vu --zk --mode interactive --target -128 --total-vus 4096 --reps 1 --batch 16384 --pipeline 2 \
   --device cuda --instance-procs 16 --instances-cache /workspace/instances-cache --out "$RD/local_fp8_b16384_p2.json" 2>&1 | grep -h "^rep " | cut -c1-200
"$PY" - "$RD/local_fp8_b16384_p2.json" <<'PYEOF'
import json,sys
r=json.load(open(sys.argv[1])); md={e["name"]:e["value"] for e in r["measurements"]}
print("LOCAL fp8 p2", {k:round(v,4) for k,v in md.items() if isinstance(v,(int,float)) and (k.startswith("t.") or k.startswith("split."))}, r["validation"]["status"])
PYEOF
