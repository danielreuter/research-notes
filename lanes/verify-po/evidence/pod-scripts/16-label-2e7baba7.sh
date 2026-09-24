#!/usr/bin/env bash
# verify-po: label the A-GKR H100 FP8 result art:2e7baba7 (evidence from 08-agkr-verify.sh, run r20260924-221801-97bc).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-2e7baba7
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:2e7baba76e89f789646de954bf63e21b6fa28df8065d45b34cf3836148997780 \
  --tree art:438ada92e2328866c4028d74ccd55bf74ef2b09cd26555618f06f21a551dff5e \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ main ab9573fd, unchanged at lane/agkr-fp8 891572a0; binary sha256 a48eac01714ecf3c), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "3/3 proofs (run-files art:438ada92 proofs/rep{0,1,2}.bin, sha256 f80ecc53...) accepted: vus 4096, units 196608, steps 48, slots 2711, msgs 8912, bytes_read 17251312, ligero_rows 21576, committed_elements 88375120; 1.45-1.62 s at 15 threads. Statement: circuit.txt / epilogue.txt / chain.txt and manifest params byte-identical to 'gpu.v2.export circuits --model hopper_e4m3_wgmma_k32' of lane/agkr-fp8@07a8edd6 (891572a0 differs from it only in bench_result.py metadata) run on my pod (main has no E4M3 A-GKR builder); public.bin (4096 words) equals pack_public(final FP32 word) of the frozen fp8-hopper set drawn by main ab9573fd, 0 mismatches. Negatives, all rejected: mutate --sample 64 (356/356), my public word +1 at VU 17, the producer's word_plus / word_minus / sign_flip / exp_plus (art:cdaabf41) with my binary (its honest case accepted)." \
  --seconds 1.62 \
  $O/verify.out $O/statement-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/mutate.log $O/neg-mine.log
