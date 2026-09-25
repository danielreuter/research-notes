#!/usr/bin/env bash
# verify-po: verdict for the A-GKR RTX 4090 FP8 merged-LK result art:45c5be4a (agkr-fp8 handoff 20260925T0045Z; evidence from
# 24-agkr-fp8-merged.sh, run r20260925-005647-bf66). HOLD=1 (default): register the verdict only, per the coordinator's hold
# (20260925T0050Z); HOLD=0 VID=art:<verdict>: write the labels from that verdict (the release).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-45c5be4a
if [ "${HOLD:-1}" = 1 ]; then MODE=(--hold); else MODE=(--vid "$VID"); fi
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:45c5be4aeef2c558bc7f8c230a2a6e6a6d0744b2a2253057a9525bf3452bdc42 "${MODE[@]}" \
  --tree art:979e37aa8826a1a97cee332a706b0d5a18eab53f21e5a669ba02fcb3c349f3a8 \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ main ab9573fd, unchanged at lane/agkr-fp8 3be6a35f; binary sha256 a48eac01714ecf3c), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "3/3 proofs (run-files art:979e37aa proofs/rep{0,1,2}.bin, sha256 c31c1cd8...) accepted: vus 4096, units 196608, steps 48, slots 727, msgs 1790, bytes_read 17966656, ligero_rows 22730, committed_elements 93101755; 1.29-1.43 s at 15 threads. Statement: circuit.txt (merged LK, 8 cols x 261819 rows) / epilogue.txt / chain.txt and manifest params byte-identical to 'gpu.v2.export circuits --model ada_e4m3_m16n8k32' of lane/agkr-fp8@3be6a35f run on my pod; public.bin equals pack_public of main's frozen fp8-ada set, 0 mismatches. Merge rewrite: the same export with --no-merge reproduces byte for byte the unmerged statement verified for art:1b4fd4a1 (request 3), and my check with main's parse_circuit (23-lk-merge-check.py) finds the dumped circuit to be exactly its tag-merge: non-lookup lines identical, 150/150 queries = key + tag*2^20, bare tag constant, outputs unchanged, zero padding, tag<->table bijective over 10 tables; LK rows = the tagged union of the 10 source tables as a multiset (261819 = 261819), first column unique and < P. Negatives, all rejected: mutate --sample 64 (356/356), my public word +1 at VU 17, the producer's 4 LK-aimed negatives (r5_key, shift_out, t_op_out, tnorm_out: 'LogUp LK level 0: final check') and word_plus / word_minus / sign_flip / exp_plus (art:f01f7196) with my binary; its honest case accepted." \
  --seconds 1.43 \
  $O/verify.out $O/statement-check.json $O/lk-merge-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/mutate.log $O/neg-mine.log \
  $O/negp-r5_key.log $O/negp-shift_out.log $O/negp-t_op_out.log $O/negp-tnorm_out.log $O/negp-honest.log
