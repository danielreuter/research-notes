#!/usr/bin/env bash
# verify-po: label the A-GKR RTX 4090 FP8 result art:ecd96143 (agkr-fp8 handoff lanes/coordinator/20260925T0006Z; unchanged
# statement, so not under the coordinator's hold; evidence from 08-agkr-verify.sh PREV=f2363663, run r20260925-010528-640f).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-ecd96143
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:ecd961433c94c2b49b06d722b0d349a73d8bb89fb1858ce1b167e18836576d61 \
  --tree art:0667ed4684083a8bb2893f31a00140fea374ffb85a43973420dcd62118c1b6d7 \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ main ab9573fd, unchanged at lane/agkr-fp8 f2363663; binary sha256 a48eac01714ecf3c), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "3/3 proofs (run-files art:0667ed46 proofs/rep{0,1,2}.bin, sha256 b5ef0238..., the same bytes as the verified art:1b4fd4a1's) accepted: vus 4096, units 196608, steps 48, slots 2881, msgs 9547, bytes_read 18152824, ligero_rows 22730, committed_elements 93101755; 1.28-1.48 s at 15 threads. Statement: circuit.txt / epilogue.txt / chain.txt and manifest params byte-identical to 'gpu.v2.export circuits --model ada_e4m3_m16n8k32' of lane/agkr-fp8@f2363663 run on my pod (the unmerged E4M3 statement of art:1b4fd4a1); public.bin equals pack_public of main's frozen fp8-ada set, 0 mismatches. Negatives, all rejected: mutate --sample 64 (356/356), my public word +1 at VU 17, the producer's word_plus / word_minus / sign_flip / exp_plus (art:9398f028) with my binary; its honest case accepted." \
  --seconds 1.48 \
  $O/verify.out $O/statement-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/mutate.log $O/neg-mine.log
