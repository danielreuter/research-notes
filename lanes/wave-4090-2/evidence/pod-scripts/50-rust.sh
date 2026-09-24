#!/usr/bin/env bash
# wave-4090-2: Rust re-verify (the pod's /workspace/bin/ligero-verify, cargo --release of main 24f252b1's backends/ligero-verify)
# of every dumped rep of the named local runs: system-digest (relation pin) then `batch --target-bits 128`; +shared pairs with
# --system-h (reverify.py does not pass it). Writes proofs/rust_digest.json and proofs/rust_batch.json (bench.summary reads the
# latter). Run only when no timing is in flight.  Usage: TAGS="bare-v3x4-p8-r2-local ..." bash 50-rust.sh
source /workspace/env.sh
V=/workspace/bin/ligero-verify
LOG=/workspace/wave-4090/rust.txt
sha256sum $V | tee -a $LOG
for t in $TAGS; do
  p=/workspace/wave-4090/runs/$t/proofs
  [ -d $p ] || { echo "$t: no proofs dir" | tee -a $LOG; continue; }
  cd $p
  h=(); [ -f system_h.bin ] && h=(--system-h system_h.bin)
  $V system-digest --system system.bin > rust_digest.json 2> rust_digest.err
  $V batch --system system.bin "${h[@]}" --dir rep1 --jobs 12 --threads 1 --target-bits 128 --json rust_batch.json > rust_batch.out 2>&1
  rc=$?
  echo "$(date -u +%H:%M:%SZ) $t rc=$rc $(tail -n 1 rust_batch.out)" | tee -a $LOG
done
