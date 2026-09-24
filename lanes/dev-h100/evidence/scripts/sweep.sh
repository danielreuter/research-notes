#!/usr/bin/env bash
# sweep.sh REL : brief §3 operating-point sweep on the BARE column, --reps 1, interactive ZK with the live verifier:
# --batch in {4096, 8192, 16384, 32768} x --pipeline in {1, 2, 4}; one result JSON per config under $RD/sweep/, one summary line each.
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
PY=/workspace/venv312/bin/python
export PYTHONPATH="$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/tools/research/src:$PWD"
RD=${RESEARCH_RUN_DIR:-/tmp}
rel=$1; shift
mkdir -p "$RD/sweep"
BATCHES=${BATCHES:-"4096 8192 16384 32768"}
PIPES=${PIPES:-"1 2 4"}
for b in $BATCHES; do
  for p in $PIPES; do
    out="$RD/sweep/${rel}_b${b}_p${p}.json"
    echo; echo "=== [$(date -u +%H:%M:%S)] $rel --batch $b --pipeline $p"
    t0=$(date +%s)
    "$PY" -m backends.direct.ligero.run --relation "$rel" bench-vu --zk --mode interactive --verifier tcp://213.173.105.69:30899 \
        --target -128 --total-vus 4096 --reps 1 --batch "$b" --pipeline "$p" --device cuda --instance-procs 16 \
        --instances-cache /workspace/instances-cache --out "$out" "$@" > "$RD/sweep/${rel}_b${b}_p${p}.log" 2>&1
    rc=$?
    w=$(( $(date +%s) - t0 ))
    if [ $rc -eq 0 ] && [ -f "$out" ]; then
      "$PY" - "$out" "$rel" "$b" "$p" "$w" <<'PYEOF'
import json, sys
r = json.load(open(sys.argv[1])); m = r.get("measurements", [])
md = {e["name"]: e["value"] for e in m} if isinstance(m, list) else dict(m)
vals = {k: md.get(k) for k in ("t.total", "t.total_live", "net.rtt_ms", "net.wait_seconds", "verify.wall_s", "peak_device_bytes")}
vals["validation"] = (r.get("validation") or {}).get("status")
print(f"SWEEP {sys.argv[2]} batch={sys.argv[3]} pipeline={sys.argv[4]} rc=0 wall={sys.argv[5]}s " + " ".join(f"{k}={v}" for k, v in vals.items()))
PYEOF
    else
      echo "SWEEP $rel batch=$b pipeline=$p rc=$rc wall=${w}s FAILED"; tail -30 "$RD/sweep/${rel}_b${b}_p${p}.log"
    fi
  done
done
echo SWEEP_DONE
