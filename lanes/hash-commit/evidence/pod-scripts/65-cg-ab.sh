#!/usr/bin/env bash
# commit-gpu harness A/B on one tree (/workspace/src): LIGERO_COMMIT_GPU=0 (host frame-v3 trees, CPU keyed-BLAKE3 chain
# witness) vs 1 (the GPU committer), same bench, alternating rounds; every run's commitment evidence sha, statement digest
# and the Rust batch verdict (auth.rs multiproofs) go to runs.txt.  REL (default fp8-ada+blake3), ROUNDS (default 3).
source /workspace/hash-commit/scripts/lib.sh
REL=${REL:-fp8-ada+blake3}; slug=$(echo $REL | tr '+' '_')
for r in $(seq ${ROUNDS:-3}); do
  LIGERO_COMMIT_GPU=0 run cg-host-$slug-r$r /workspace/src $REL ${BATCH:-8192} ${DEPTH:-4} ${REPS:-5}
  LIGERO_COMMIT_GPU=1 run cg-gpu-$slug-r$r /workspace/src $REL ${BATCH:-8192} ${DEPTH:-4} ${REPS:-5}
done
