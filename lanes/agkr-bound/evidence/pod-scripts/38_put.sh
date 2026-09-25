#!/usr/bin/env bash
# agkr-bound: register the FP8 link build run (37 -> 31 on fp8-hopper+sha256, unpinned commitment), push the two
# non-custody runs, then the remote reindex from the pod.  usage: bash 38_put.sh
set -euo pipefail
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
IN=$RESEARCH_RUN_DIR/inputs
R=/workspace/research/runs
A=/workspace/agkr-bound
RUNS="r20260925-114542-3ca4 r20260925-114925-2f5c"
T=$A/link-evidence-fp8; rm -rf $T; mkdir -p $T/runs $T/rust
for r in $RUNS; do cp $R/$r/stdout.log $T/runs/$r.stdout.log; done
cp $IN/37_fp8_link.sh $IN/31_link_rust.py $IN/31_link_rust.sh $T/
L=$A/link-rust-fp8-hopper
cp $L/link_build.json $T/
for d in $L/*/; do n=$(basename $d); [ -f $d/rust.json ] && cp $d/rust.json $T/rust/$n.json; done
du -sh $T
bash $IN/04_store.sh put $T '{"lane": "agkr-bound", "what": "A-GKR sigma-form bit link on FP8 (fp8-hopper, sha256 row leaves, UNPINNED commitment, --allow-unpinned-commitment), the 78b1a62e build. A100 vy-agkr-bound2, 4,096 VUs, 1 warm-up + 3 reps, MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1e12: median prove 0.6068 -> 0.7782 s (link 0.178 s), Python verify 0.489 -> 0.648 s, Rust verify 1.706 -> 2.360/2.337 s (+0.219 s derivation at load), proof +6,144 B; 11 of 11 negatives rejected by both verifiers, honest and honest_nolink accepted. Run r20260925-114542-3ca4 is the same build with the Rust side refused on the unpinned commitment (policy, not a link result). Drill-down only (L).", "run_id": "r20260925-114925-2f5c", "source_commit": "78b1a62e", "candidate": "A-GKR", "variant": "route (a) sigma-form link, prime side, fp8"}' --ref link_build=art:bd3d8b2c
bash $IN/04_store.sh push $RUNS
bash $IN/04_store.sh reindex 2>&1 | tail -5
