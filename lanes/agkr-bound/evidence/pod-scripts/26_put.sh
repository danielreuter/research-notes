#!/usr/bin/env bash
# agkr-bound: register the fp8 in-unit link run (20, fp8-hopper+blake3), the dense-check kernels (23 fused Triton, 24 int8
# tensor-core coefficients) and gap_alt_operand against the link's prime-side checks (25), then preserve the runs.
# usage: bash 26_put.sh
set -euo pipefail
IN=$RESEARCH_RUN_DIR/inputs
R=/workspace/research/runs
A=/workspace/agkr-bound
RUNS="r20260925-093651-1bfd r20260925-094007-fd9e r20260925-094400-b761 r20260925-094840-969f r20260925-095534-ad8c"
T=$A/link-evidence-2; rm -rf $T; mkdir -p $T/runs
for r in $RUNS; do cp $R/$r/stdout.log $T/runs/$r.stdout.log; done
cp $IN/23_dense_triton.py $IN/24_dense_tc.py $IN/25_gap_dense.py $IN/25_gap_dense.sh $T/
L=$A/link-unit-fp8-hopper
cp $L/link_unit.json $T/fp8_link_unit.json
for c in honest bit_flip non_boolean alt_honest_bits alt_alt_bits; do mkdir -p $T/fp8-unit-$c; cp $L/$c/verify_sc.json $L/$c/commitment.txt $T/fp8-unit-$c/; done
cp $A/dense/dense_triton.json $A/dense/dense_tc_*.json $T/
for c in bf16-ampere-sha256 fp8-hopper-blake3; do cp $A/gap-dense/$c/gap_dense.json $T/gap_dense_$c.json; done
du -sh $T
bash $IN/04_store.sh put $T '{"lane": "agkr-bound", "what": "A-GKR route (a) prime-side costs, part 2 (A100 vy-agkr-bound2, frozen bench-instances/v1, 4,096 VUs; benchmarks + scaffold only, the cross-field link NOT built, coordinator 0922Z; no cell counts). (1) fp8-hopper+blake3 link bits in-unit (8 bits per operand code): median prove 0.391 -> 0.600 s (+54%), committed 88.5M -> 189M; bit_flip / non_boolean / alt_honest_bits rejected, alt_alt_bits accepted (Rust + Python). (2) dense GF(2^128) check at N = 201,326,592 bits, one challenge point: fused Triton (eq doubling + byte-table coefficients + inner product) 0.367 s (eq 0.023, coef+ip 0.345); int8 tensor-core coefficients (bits[B,128] x rho in 7-bit limbs, BLOCK 256) 0.066 s (eq 0.023, coef+ip 0.044); both cross-checked against the torch reference (0.875 s). (3) gap_alt_operand vs the link prime-side checks, bf16-ampere+sha256 and fp8-hopper+blake3: the altered operand changes 1 link bit; its x-row leaf digest != committed (binary side can only open the honest preimage); honest bits: all 128 planes S_t = 2u_t + z_t, BabyBear^6 combination 0; altered bits: 62/128 (BF16), 69/128 (fp8) planes parity-mismatched, combination nonzero. The operand-to-message bit layout is taken as given (not built).", "run_id": "r20260925-095534-ad8c", "source_commit": "86f86084", "candidate": "A-GKR", "variant": "route (a) prime-side cost model"}' --ref link_costs=art:35bce6f5 --ref scaffold=art:f2f07e3c
bash $IN/04_store.sh push $RUNS
