#!/usr/bin/env bash
# Lane tier0-bytes: Rust `ligero-verify batch` over every dumped rep1 tree (13 sub-batches, 13 jobs x 1 thread), 3 timed reps each.
# (measure.sh's inline verify step used /usr/bin/time, which the pod image lacks; this is that step.)
set -uo pipefail
ROOT=/workspace/t0b
CELLS=${CELLS:-"hash_before hash_after bare_before bare_after"}
for item in $CELLS; do
  OUT=$ROOT/$item
  [ -d "$OUT/dump/rep1" ] || { echo "$item: no dump"; continue; }
  for r in 1 2 3; do
    t0=$(date +%s.%N)
    /workspace/bin/ligero-verify batch --system "$OUT/dump/system.bin" --dir "$OUT/dump/rep1" --jobs 13 --threads 1 --target-bits 128 \
        --json "$OUT/verify_$r.json" > "$OUT/verify_$r.log" 2>&1
    rc=$?
    t1=$(date +%s.%N)
    echo "$item verify rep $r rc=$rc wall=$(python3 -c "print(f'{$t1-$t0:.3f}')") s :: $(head -c 300 "$OUT/verify_$r.log" | tr '\n' ' ')"
  done
done 2>&1 | tee "$ROOT/verify_summary.txt"
