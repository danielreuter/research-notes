#!/usr/bin/env bash
# Lane tier0-bytes: before/after of the trimmed hashed statement (LIGSTM06) on the reference RTX 4090.
# fp8-ada bare and fp8-ada+hash, ZK interactive, LOCAL coins, 4096 VUs, --batch 16384 (13 sub-batches, l = 16384), --pipeline 4,
# 3 reps, rep 1 dumped; then `ligero-verify batch` over the dump (13 jobs x 1 thread, --reps 3 for the verify time).
# "before" = LIGERO_STMT_TRIM=0 (the v5 writer, byte-identical to main e0cf2cd); "after" = the default (v6).  Same tree a264152, same binaries.
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
SRC=/workspace/src
PY=/workspace/venv312/bin/python
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
export OMP_NUM_THREADS=16
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
ROOT=/workspace/t0b
LOG=$ROOT/commands.log
CACHE="--instance-procs 16 --instances-cache /workspace/instances-cache"
PIPE=${PIPE:-4}
cd "$SRC"
mkdir -p "$ROOT"
CELLS=${CELLS:-"hash_before hash_after bare_before bare_after"}
for item in $CELLS; do
  rel=${item%_*}; phase=${item#*_}
  OUT=$ROOT/$item; mkdir -p "$OUT"
  AUTH=""; [ "$rel" = hash ] && AUTH="--auth included-hash"
  TRIM=1; [ "$phase" = before ] && TRIM=0
  t0=$(date -u +%s)
  echo "[$(date -u +%H:%M:%SZ)] ($item) START trim=$TRIM pipeline=$PIPE" | tee -a "$LOG"
  LIGERO_STMT_TRIM=$TRIM "$PY" -m backends.direct.ligero.run --relation fp8-ada bench-vu --zk --mode interactive --target -128 \
      --total-vus 4096 --batch 16384 --pipeline $PIPE --reps 3 --device cuda $CACHE $AUTH \
      --dump-dir "$OUT/dump" --dump-reps 1 --out "$OUT/result.json" > "$OUT/run.log" 2>&1
  rc=$?
  echo "[$(date -u +%H:%M:%SZ)] ($item) EXIT=$rc  elapsed=$(( $(date -u +%s) - t0 ))s" | tee -a "$LOG"
  # bytes of the dump
  ( cd "$OUT/dump" && ls -la system.bin manifest.json 2>/dev/null; du -b rep1/*.proof | awk '{s+=$1} END {print "proof_bytes_total", s, NR}';
    du -b rep1/*.stmt | awk '{s+=$1} END {print "stmt_bytes_total", s, NR}'; head -c 8 rep1/sub_00.stmt | od -c | head -1;
    du -b rep1/*.coins 2>/dev/null | awk '{s+=$1} END {print "coins_bytes_total", s, NR}' ) | tee "$OUT/bytes.txt"
  # Rust verify (own coins from the .coins files, as the batch tool does), timed 3x
  for r in 1 2 3; do
    /workspace/bin/ligero-verify batch --system "$OUT/dump/system.bin" --dir "$OUT/dump/rep1" \
        --jobs 13 --threads 1 --target-bits 128 --json "$OUT/verify_$r.json" > "$OUT/verify_$r.log" 2>&1
    echo "verify rep $r rc=$?"; head -c 400 "$OUT/verify_$r.log"; echo; tail -1 "$OUT/verify_$r.log"
  done | tee "$OUT/verify.txt"
  "$PY" - "$OUT/result.json" "$item" <<'PYEOF'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as e:
    print(sys.argv[2], "NO RESULT:", e); sys.exit(0)
m = {x["name"]: x["value"] for x in d.get("measurements", [])}
keys = ("t.total", "t.serialization", "split.openings_seconds", "split.subbatches", "verifier.seconds", "mem.peak_device_bytes", "proof_bytes")
print(sys.argv[2], " ".join(f"{k}={m.get(k)}" for k in keys))
b = d.get("backend", {})
print("  backend:", {k: b.get(k) for k in ("statement_format", "pipeline", "authentication", "hash")})
reps = d.get("reps") or d.get("raw", {}).get("reps")
print("  reps:", reps if reps else "(see result.json)")
PYEOF
done 2>&1 | tee -a "$ROOT/summary.txt"
echo MEASURE_DONE | tee -a "$LOG"
