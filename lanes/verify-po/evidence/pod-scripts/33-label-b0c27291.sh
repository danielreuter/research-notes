#!/usr/bin/env bash
# verify-po: label the A-GKR H100 FP8 result art:b0c27291 (agkr-fp8 handoff 20260925T0203Z; unchanged statement, so not under the
# coordinator's hold; evidence from 08-agkr-verify.sh PREV=a97576b5 EXPORT_ARGS=--no-merge, run r20260925-020532-8dac).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-b0c27291
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:b0c27291de3ed71c08219d428c7bca4678c0506842c959fcccb26ed70c3b1d71 \
  --tree art:25c57ccb8815d411bcb985633dbcbe75ed3e3bcc11bb2916c19e1f93970e5b83 \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ main ab9573fd, unchanged at lane/agkr-fp8 a97576b5; binary sha256 a48eac01714ecf3c), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "3/3 proofs (run-files art:25c57ccb proofs/rep{0,1,2}.bin, sha256 f80ecc53..., byte-identical to the verified art:2e7baba7's, as are all statement files) accepted: vus 4096, units 196608, steps 48, slots 2711, msgs 8912, bytes_read 17251312, ligero_rows 21576, committed_elements 88375120; 0.95-1.07 s at 15 threads. Statement: circuit.txt / epilogue.txt / chain.txt and manifest params byte-identical to 'gpu.v2.export circuits --model hopper_e4m3_wgmma_k32 --no-merge' of lane/agkr-fp8@a97576b5 run on my pod (the unmerged statement of art:2e7baba7); public.bin equals pack_public of main's frozen fp8-hopper set, 0 mismatches. Negatives, all rejected: mutate --sample 64 (356/356), my public word +1 at VU 17, the producer's word_plus / word_minus / sign_flip / exp_plus (art:07b5adb8) with my binary; its honest case accepted." \
  --seconds 1.07 \
  $O/verify.out $O/statement-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/mutate.log $O/neg-mine.log
