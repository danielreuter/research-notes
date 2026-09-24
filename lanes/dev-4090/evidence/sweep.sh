#!/usr/bin/env bash
# Lane dev-4090: operating-point sweep (brief §3), fp8-ada BARE, ZK interactive, live verifier, 4096 VUs, --reps 1.
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
SRC=/workspace/src
PY=/workspace/venv312/bin/python
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
export OMP_NUM_THREADS=16
LOG=/workspace/d4090/commands.log
CACHE="--instance-procs 16 --instances-cache /workspace/instances-cache"
LIVE="tcp://213.173.105.69:30899"
cd "$SRC"
mkdir -p /workspace/d4090/sweep
BATCHES=${BATCHES:-"16384 32768 8192 4096"}
PIPES=${PIPES:-"1 2 4"}
for B in $BATCHES; do for P in $PIPES; do
  item="sweep_b${B}_p${P}"
  OUT=/workspace/d4090/sweep/$item
  mkdir -p "$OUT"
  t0=$(date -u +%s)
  echo "[$(date -u +%H:%M:%SZ)] ($item) START" | tee -a "$LOG"
  "$PY" -m backends.direct.ligero.run --relation fp8-ada bench-vu --zk --mode interactive --verifier $LIVE --target -128 \
      --total-vus 4096 --batch $B --pipeline $P --reps 1 --device cuda $CACHE --out "$OUT/result.json" > "$OUT/run.log" 2>&1
  rc=$?
  echo "[$(date -u +%H:%M:%SZ)] ($item) EXIT=$rc  elapsed=$(( $(date -u +%s) - t0 ))s" | tee -a "$LOG"
  "$PY" - "$OUT/result.json" "$item" <<'PYEOF'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as e:
    print(sys.argv[2], "NO RESULT:", e); sys.exit(0)
m = {x["name"]: x["value"] for x in d.get("measurements", [])}
keys = ("t.total", "t.total_live", "net.rtt_ms", "net.wait_seconds", "verify.wall_s", "split.subbatches", "mem.peak_device_bytes", "proof_bytes")
print(sys.argv[2], " ".join(f"{k}={m.get(k)}" for k in keys), "validation=", d.get("validation", {}).get("status") if isinstance(d.get("validation"), dict) else d.get("validation"))
PYEOF
done; done | tee -a /workspace/d4090/sweep/summary.txt
