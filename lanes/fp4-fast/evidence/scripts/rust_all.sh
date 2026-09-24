#!/bin/bash
export PATH=/root/.cargo/bin:$PATH
for r in "$@"; do
  d=/workspace/research/runs/$r/proofs
  [ -f $d/rust_batch_rep1.json ] && { echo "$r already"; continue; }
  /workspace/bin/ligero-verify batch --system $d/system.bin --dir $d/rep1 --jobs 8 --threads 1 --target-bits 128 --json $d/rust_batch_rep1.json 2>&1 | tail -1 | cut -c1-140 | sed "s/^/$r: /"
done
