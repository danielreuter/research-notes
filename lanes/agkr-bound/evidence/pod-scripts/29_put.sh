#!/usr/bin/env bash
# agkr-bound: register the link layout check (27) and the dense check folded into the real in-unit proof (28), then
# preserve the runs.  usage: bash 29_put.sh
set -euo pipefail
IN=$RESEARCH_RUN_DIR/inputs
R=/workspace/research/runs
A=/workspace/agkr-bound
RUNS="r20260925-100729-6578 r20260925-101520-bc72"
T=$A/link-evidence-3; rm -rf $T; mkdir -p $T/runs
for r in $RUNS; do cp $R/$r/stdout.log $T/runs/$r.stdout.log; done
cp $IN/27_layout.py $IN/27_layout.sh $IN/28_link_dense.py $IN/28_link_dense.sh $T/
for c in bf16-ampere-sha256 fp8-hopper-blake3; do cp $A/layout/$c/layout.json $T/layout_$c.json; done
cp $A/link-dense-bf16-ampere/link_dense.json $T/
du -sh $T
bash $IN/04_store.sh put $T '{"lane": "agkr-bound", "what": "A-GKR route (a) prime side, part 3 (A100 vy-agkr-bound2, frozen bench-instances/v1, 4,096 VUs; benchmarks + scaffold only, pod scripts, the cross-field link NOT built, no cell counts; MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1e12 set). (1) layout: unit u = v*U + s (U = 96 BF16 / 48 fp8) consumes x[v, k s .. k s + k - 1] and W column v the same words, every operand word exactly once: the link map unit bits -> leaf value bits is a bijection (201,326,592 BF16 / 100,663,296 fp8 bits); sha256/row/v1 value starts after one 64-byte prefix block (block-aligned, 50 compressions, 49 with the prefix midstate); blake3-keyed/row/v2 no prefix. (2) the dense GF(2^128) check as one more term of A-GKR batched Ligero functional (wraps ligero.prove_open / verify_open: eq(r,i) from the transcript, plane sums S_t, u_t absorbed as a stand-in for its commitment, rho_t, a += c at the link-bit positions; verifier b += sum rho_t (2u_t + z_t), z a stand-in from the honest message bits) on the real bf16-ampere+sha256 in-unit proof: median prove 1.201 -> 1.413 s (link term 0.211 s), Python verify 1.246 -> 1.469 s (link term 0.155 s); gap_alt_operand accepted without the term, REJECTED with it (ligero: linear functional value mismatch).", "run_id": "r20260925-101520-bc72", "source_commit": "86f86084", "candidate": "A-GKR", "variant": "route (a) prime-side cost model"}' --ref link_costs_2=art:64220e14 --ref link_costs=art:35bce6f5
bash $IN/04_store.sh push $RUNS
