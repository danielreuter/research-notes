#!/usr/bin/env bash
# verify-po: label the A-GKR RTX 4090 FP8 result art:1b4fd4a1 (evidence from 08-agkr-verify.sh, run r20260924-215649-a2c4).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-1b4fd4a1
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:1b4fd4a17e9023258e502169b2ec156dc084393cddf284616a0642a3e645d6e2 \
  --tree art:89a2ce85c4550ca004c76bcc9ba82eb4edb182f4d6961b459c252eb16c9f406c \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ main ab9573fd, unchanged at lane/agkr-fp8 07a8edd6; binary sha256 a48eac01714ecf3c), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "3/3 proofs (run-files art:89a2ce85 proofs/rep{0,1,2}.bin, sha256 b5ef0238...) accepted: vus 4096, units 196608, steps 48, slots 2881, msgs 9547, bytes_read 18152824, ligero_rows 22730, committed_elements 93101755; 1.41-1.81 s at 15 threads. Statement: circuit.txt / epilogue.txt / chain.txt and manifest params byte-identical to lane/agkr-fp8@07a8edd6's 'gpu.v2.export circuits --model ada_e4m3_m16n8k32' run on my pod (main has no E4M3 A-GKR builder); public.bin (4096 words) equals pack_public(final FP32 word) of the frozen fp8-ada set drawn by main ab9573fd, 0 mismatches. Negatives, all rejected: mutate --sample 64 (356/356), my public word +1 at VU 17, the producer's word_plus / word_minus / sign_flip / exp_plus (art:edfbca4d) with my binary (its honest case accepted)." \
  --seconds 1.81 \
  $O/verify.out $O/statement-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/mutate.log $O/neg-mine.log
