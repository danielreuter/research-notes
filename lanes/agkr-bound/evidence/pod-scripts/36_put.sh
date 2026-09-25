#!/usr/bin/env bash
# agkr-bound: register the final link build run (31 with vu_remap) as an addendum to art:bd3d8b2c.  usage: bash 36_put.sh
set -euo pipefail
IN=$RESEARCH_RUN_DIR/inputs
R=/workspace/research/runs
A=/workspace/agkr-bound
RUNS="r20260925-113047-d490"
T=$A/link-evidence-5; rm -rf $T; mkdir -p $T/runs $T/rust
for r in $RUNS; do cp $R/$r/stdout.log $T/runs/$r.stdout.log; done
cp $IN/31_link_rust.py $IN/31_link_rust.sh $T/
L=$A/link-rust-bf16-ampere
cp $L/link_build.json $T/
for d in $L/*/; do n=$(basename $d); [ -f $d/rust.json ] && cp $d/rust.json $T/rust/$n.json; done
du -sh $T
bash $IN/04_store.sh put $T '{"lane": "agkr-bound", "what": "A-GKR sigma-form bit link, final build run at 78b1a62e (addendum to art:bd3d8b2c: the same statement and cases plus vu_remap, the red team negative 7: the prover computes sigma under Lambda with VUs 0 and 1 swapped, honest witness -> rejected by Python and Rust, sigma_3 parity). A100 vy-agkr-bound2, bf16-ampere+sha256 in-unit, 4,096 VUs, 1 warm-up + 3 reps, MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1e12: median prove 1.1994 -> 1.5286 s (link 0.333 s), Python verify 1.261 -> 1.564 s, Rust verify 3.414 -> 4.676/4.719 s (+0.436 s derivation at load); 11 of 11 negatives rejected by both verifiers, honest and honest_nolink accepted. Drill-down only (L).", "run_id": "r20260925-113047-d490", "source_commit": "78b1a62e", "candidate": "A-GKR", "variant": "route (a) sigma-form link, prime side"}' --ref link_build=art:bd3d8b2c
bash $IN/04_store.sh push $RUNS
