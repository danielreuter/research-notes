#!/usr/bin/env bash
# agkr-bound: register the built sigma-form bit link (30-34) and preserve the runs.  usage: bash 35_put.sh
set -euo pipefail
IN=$RESEARCH_RUN_DIR/inputs
R=/workspace/research/runs
A=/workspace/agkr-bound
RUNS="r20260925-104121-b263 r20260925-105059-259d r20260925-105607-10ec r20260925-105818-9514 r20260925-110118-a1a8 r20260925-111118-2c83 r20260925-111244-a13f r20260925-111706-2643 r20260925-111843-37b0 r20260925-112019-a85e r20260925-112412-a19c"
T=$A/link-evidence-4; rm -rf $T; mkdir -p $T/runs $T/rust
for r in $RUNS; do cp $R/$r/stdout.log $T/runs/$r.stdout.log; done
cp $IN/3[0-4]_*.py $IN/3[0-4]_*.sh $T/
L=$A/link-rust-bf16-ampere
cp $L/link_build.json $T/
for d in $L/*/; do n=$(basename $d); [ -f $d/rust.json ] && cp $d/rust.json $T/rust/$n.json; [ -f $d/link.txt ] && cp $d/link.txt $T/rust/$n.link.txt; done
sha256sum $L/honest/proof.bin $L/honest/x.bin $L/honest/w.bin $L/honest/circuit.txt $L/honest/commitment.txt > $T/honest_sha256.txt
du -sh $T
bash $IN/04_store.sh put $T '{"lane": "agkr-bound", "what": "A-GKR route (a) prime side BUILT (lane/agkr-bound 78b1a62e: gpu/link.py, verifier/src/link.rs, PROTOCOL 17): sigma form (red team S1, NON_ZK_PROOF only), one GF(2^256) point (C1), m = 28 whole-digest coins after both roots, Lambda_F derived by both verifiers from the unit circuit and checked bijective, booleanity + recomposition checked per link bit, 0 <= sigma_t <= n_cells and parity = bit_t(y), the 256 constraints as one dense term of the batched Ligero functional. Binary side a STAND-IN (root_b = SHA-256(TAG, commitment.txt); y from x.bin/w.bin, which the Rust verifier requires to hash to the public sha256/row/v1 digests). A100 vy-agkr-bound2, bf16-ampere+sha256 in-unit statement, frozen bench-instances/v1, 4,096 VUs, 1 warm-up + 3 reps, MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1e12 set. Final (r20260925-112019-a85e): median prove 1.2016 -> 1.5418 s (+0.340 s; link breakdown r20260925-112412-a19c: eq table 0.137, z 0.010, fused y+sigma plane sums 0.062, term of a 0.124), Python verify 1.249 -> 1.575 s, Rust verify (13 threads, EPYC 7742) 3.419 -> 4.665 s plus 0.435 s Lambda_F derivation at statement load, proof +6,144 B (256 messages). Negatives rejected by Python AND Rust: bit_flip, non_boolean, alt_alt_bits (altered operand with its own bits), sigma_range, sigma_plus2, root_b_changed, z_differs (Rust: x.bin no longer hashes to the public digest), S dup_cell, S no_booleanity; honest and honest_nolink accepted. Drill-down only (L) until C3 (Flock 2^-128) and C4 (chain glue); forged-middle-block negative needs the Flock side.", "run_id": "r20260925-112019-a85e", "source_commit": "78b1a62e", "candidate": "A-GKR", "variant": "route (a) sigma-form link, prime side"}' --ref link_costs_3=art:400126e2 --ref link_costs_2=art:64220e14
bash $IN/04_store.sh push $RUNS
