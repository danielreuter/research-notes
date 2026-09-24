#!/usr/bin/env bash
# local3.sh: drill-down, NOT Table 2: the two bare relations at their live operating point, interactive ZK with LOCAL coins (no --verifier), --reps 3, dumps rep1;
# then pytest backends/direct/ligero with OMP_NUM_THREADS=16 (the bootstrap's run oversubscribed the 22-core cgroup quota).
set -uo pipefail
PY=/workspace/venv312/bin/python
export PYTHONPATH="$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/tools/research/src:$PWD"
RD=${RESEARCH_RUN_DIR:-/tmp}
for cfg in "bf16-hopper 16384 2" "bf16-hopper 16384 4" "fp8-hopper 16384 4"; do
  set -- $cfg; rel=$1; b=$2; p=$3
  out="$RD/local3_${rel}_b${b}_p${p}.json"
  echo "=== [$(date -u +%H:%M:%S)] LOCAL $rel --batch $b --pipeline $p --reps 3"
  "$PY" -m backends.direct.ligero.run --relation "$rel" bench-vu --zk --mode interactive --target -128 --total-vus 4096 --reps 3 --batch $b --pipeline $p \
     --device cuda --instance-procs 16 --instances-cache /workspace/instances-cache --out "$out" --dump-dir "$RD/proofs_${rel}_p${p}" --dump-reps 1 > "$RD/local3_${rel}_b${b}_p${p}.log" 2>&1
  echo "rc=$?"; grep -h "^rep " "$RD/local3_${rel}_b${b}_p${p}.log" | cut -c1-200
  "$PY" - "$out" <<'PYEOF'
import json,sys
r=json.load(open(sys.argv[1])); md={e["name"]:e["value"] for e in r["measurements"]}
print("LOCAL3", sys.argv[1].split("/")[-1], {k:round(v,4) for k,v in md.items() if isinstance(v,(int,float)) and (k.startswith("t.") or k.startswith("split.") or k in ("proof_bytes","mem.peak_device_bytes","overhead.vs_native_peak"))}, r["validation"]["status"])
PYEOF
done
echo "=== [$(date -u +%H:%M:%S)] pytest OMP_NUM_THREADS=16"
OMP_NUM_THREADS=16 MKL_NUM_THREADS=16 "$PY" -m pytest backends/direct/ligero -q -x -p no:cacheprovider --ignore=backends/direct/ligero/privsel --durations=8 > "$RD/pytest_omp16.log" 2>&1
echo "PYTEST_OMP16 rc=$?"; tail -14 "$RD/pytest_omp16.log"
