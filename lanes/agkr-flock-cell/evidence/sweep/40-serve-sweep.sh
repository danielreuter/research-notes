#!/usr/bin/env bash
# cell-verifier (non-producer): the route (a) sweep's live Flock verifier. For each size in SIZES, in order, serve
# SESSIONS sessions of that size's statement (inputs/leaf_digests-<v>.bin, inputs/cell-<v>.json), then move on.
# A size gets at most PER_SIZE_TIMEOUT seconds.   env: SIZES="1024 4096 8192 16384 32768" SESSIONS=5 OPERATOR=cell-verifier
set -uo pipefail
B=/workspace/flock-link/flock/target/release/flock-link
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
sha256sum $B | tee $O/binary.sha256
for v in ${SIZES:-1024 4096 8192 16384 32768}; do
  [ -f $I/cell-$v.json ] || { echo "no statement for $v"; continue; }
  PC=$(python3 -c "import json;print(json.load(open('$I/cell-$v.json'))['prime_commitment'])")
  echo "== $v $(date -u +%H:%M:%S)"
  timeout ${PER_SIZE_TIMEOUT:-1500} $B cell-serve --listen 0.0.0.0:7200 --out $O/sessions-$v --vus $v --digests $I/leaf_digests-$v.bin \
    --prime-commitment $PC --operator ${OPERATOR:-cell-verifier} --sessions ${SESSIONS:-5} 2>&1 | tee $O/serve-$v.log
  echo "rc=$? $v $(date -u +%H:%M:%S)"
done
true
