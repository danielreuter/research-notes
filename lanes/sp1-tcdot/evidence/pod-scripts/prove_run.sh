#!/usr/bin/env bash
# One bare-prove run of the modified-SP1 (TC_DOT chip) host on the fork's BF16 sp1-gpu-server.
#   prove_run.sh <out-dir> <lo> <hi> <reps> <warmup-vus> <vus-per-read> [extra host args...]
set -euo pipefail
W=/workspace/sp1-tcdot
MAN=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
OUT=$1 LO=$2 HI=$3 REPS=$4 WARM=$5 PER=$6
shift 6
H=${VERITY_TCDOT_HOST:-$W/target-tcdot/release/verity-tcdot-host}
mkdir -p "$OUT"
# the fork's server (both TC_DOT chips) is $HOME/.sp1/bin/sp1-gpu-server for this process only
export HOME=$W/home-bf16 SP1_PROVER=cuda RUST_LOG=${RUST_LOG:-info}
echo "[$(date -u +%H:%M:%S)] bare-prove [$LO,$HI) reps $REPS warmup $WARM per $PER $*" | tee "$OUT/cmd.txt"
( nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used --format=csv,noheader -l 1 > "$OUT/gpu.csv" ) &
SMI=$!
/usr/bin/time -v "$H" bare-prove --instances $W/bi --manifest-sha256 $MAN --lo "$LO" --hi "$HI" --reps "$REPS" \
  --warmup-vus "$WARM" --vus-per-read "$PER" --out-dir "$OUT/proofs" "$@" > "$OUT/events.jsonl" 2> "$OUT/stderr.log" || echo "RC=$?"
kill $SMI 2>/dev/null || true
grep '^{' "$OUT/events.jsonl" | python3 -c '
import json, sys
for line in sys.stdin:
    d = json.loads(line)
    if d.get("event") == "execute":
        r = d["report"]; print("execute", r["total_cycles"], "cycles", r["routing"])
    elif d.get("event") == "rep":
        print("rep", d["rep"], "prove", round(d["prove_seconds"], 3), "save", round(d["save_seconds"], 3), "verify", round(d["verify_seconds"], 3), "shards", d["shards"], "bytes", d["proof_bytes"], "accepted", d["accepted"])
    elif d.get("event") in ("setup", "warmup"):
        print(d["event"], {k: v for k, v in d.items() if k in ("setup_seconds", "prove_seconds", "vus", "vk_hash", "elf_sha256")})
'
awk -F', ' '{gsub(/ %/,"",$2); gsub(/ MiB/,"",$3); if ($3+0 > m) m = $3+0; s += $2; n++} END {print "gpu mean util", (n ? s/n : 0), "% peak MiB", m}' "$OUT/gpu.csv"
grep -E "Maximum resident|Elapsed" "$OUT/stderr.log" | tail -2
echo "[$(date -u +%H:%M:%S)] done"
