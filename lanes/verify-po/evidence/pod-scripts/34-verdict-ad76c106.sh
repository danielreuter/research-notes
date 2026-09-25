#!/usr/bin/env bash
# verify-po: verdict for the A-GKR H100 FP8 merged-LK result art:ad76c106 (agkr-fp8 handoff 20260925T0203Z; same statement and proof
# bytes as art:3ae971dd; evidence from 24-agkr-fp8-merged.sh PREV=a97576b5, run r20260925-020532-8dac).
# HOLD=1 (default): verdict only (coordinator 20260925T0050Z); HOLD=0 VID=art:<verdict>: the release.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-ad76c106
if [ "${HOLD:-1}" = 1 ]; then MODE=(--hold); else MODE=(--vid "$VID"); fi
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:ad76c1062a287b985b6974f30bfb64e785173366da27d0f36370a2379affba3e "${MODE[@]}" \
  --tree art:55eb421ddcb57aa7d8880822530126fcc3fc5e2eddaf0ca95cc09262a51b660e \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ main ab9573fd, unchanged at lane/agkr-fp8 a97576b5; binary sha256 a48eac01714ecf3c), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "3/3 proofs (run-files art:55eb421d proofs/rep{0,1,2}.bin, sha256 0021aa91..., byte-identical to art:3ae971dd's run-files art:0c23dfc9, as are all statement files) accepted: vus 4096, units 196608, steps 48, slots 703, msgs 1703, bytes_read 17078296, ligero_rows 21576, committed_elements 88375120; 0.87 s at 15 threads. Statement: circuit.txt (merged LK, 261968 rows) / epilogue.txt / chain.txt and manifest params byte-identical to 'gpu.v2.export circuits --model hopper_e4m3_wgmma_k32' of lane/agkr-fp8@a97576b5 run on my pod; public.bin equals pack_public of main's frozen fp8-hopper set, 0 mismatches. Merge rewrite: --no-merge reproduces byte for byte the unmerged statement verified for art:2e7baba7, and 23-lk-merge-check.py (main's parse_circuit) finds the dump to be exactly its tag-merge (139/139 queries, 10 tables, 261968 rows as a multiset, first column unique and < P). Negatives, all rejected: mutate --sample 64 (356/356), my public word +1 at VU 17, the producer's 4 LK-aimed negatives (r6_key, shift_out, t_op_out, tnorm_out) and word_plus / word_minus / sign_flip / exp_plus (art:70bbba68) with my binary; its honest case accepted." \
  --seconds 0.87 \
  $O/verify.out $O/statement-check.json $O/lk-merge-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/mutate.log $O/neg-mine.log \
  $O/negp-r6_key.log $O/negp-shift_out.log $O/negp-t_op_out.log $O/negp-tnorm_out.log $O/negp-honest.log
