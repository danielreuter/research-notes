#!/usr/bin/env bash
# fill-consumer, RTX 5090, tree 444084d3 (fp4/hashed names the frozen NVFP4 set): column 2 again, the chosen config
# fp4-nvf4+poseidon2 --auth included-hash l=8192 p8, 3 local rounds (--reps 5), a fresh auth cache (the tree bindings hash
# the dataset / tier), then the pinned Rust check of each rep-1 dump and the instances block against the frozen ref.
source /workspace/fill-consumer/scripts/lib.sh
H="--auth included-hash --auth-cache /workspace/auth-cache-fp4h-frozen"
run warm-F-h-l8192-p8 local fp4-nvf4+poseidon2 8192 8 1 $H
for r in 1 2 3; do run F-h-l8192-p8-r$r local fp4-nvf4+poseidon2 8192 8 5 $H; done
for r in 1 2 3; do
  d=$O/F-h-l8192-p8-r$r
  /workspace/bin/ligero-verify batch --dir $d/proofs/rep1 --system $d/proofs/system.bin --target-bits 128 > $d/rust_batch.txt 2>&1
  echo "F-h-l8192-p8-r$r rust rc=$? $(tail -1 $d/rust_batch.txt | cut -c1-300)" | tee -a $LOG
  $PY -c "import json,sys; print(json.load(open(sys.argv[1]))['workload_fingerprint']['instances'])" $d/result.json | tee -a $LOG
done
echo "COL2_FIXED_DONE" | tee -a $LOG
