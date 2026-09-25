#!/usr/bin/env bash
# verify-po: verdict for the A-GKR H100 FP8 merged-LK result art:3ae971dd (agkr-fp8 handoff 20260925T0132Z; evidence from
# 24-agkr-fp8-merged.sh, run r20260925-013458-825f). HOLD=1 (default): register the verdict only, per the coordinator's hold
# (20260925T0050Z); HOLD=0 VID=art:<verdict>: write the labels from that verdict (the release).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-3ae971dd
if [ "${HOLD:-1}" = 1 ]; then MODE=(--hold); else MODE=(--vid "$VID"); fi
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:3ae971dd97799d842007bae866a735cd1324b50aba8e0af408b36b278172213b "${MODE[@]}" \
  --tree art:0c23dfc94b3a0651d74e57c220ae5b9c632c56661eb79ad918a2f5e46b8ed1bb \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ main ab9573fd, unchanged at lane/agkr-fp8 3be6a35f; binary sha256 a48eac01714ecf3c), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "3/3 proofs (run-files art:0c23dfc9 proofs/rep{0,1,2}.bin, sha256 0021aa91...) accepted: vus 4096, units 196608, steps 48, slots 703, msgs 1703, bytes_read 17078296, ligero_rows 21576, committed_elements 88375120; 1.06-1.17 s at 15 threads. Statement: circuit.txt (merged LK, 261968 rows) / epilogue.txt / chain.txt and manifest params byte-identical to 'gpu.v2.export circuits --model hopper_e4m3_wgmma_k32' of lane/agkr-fp8@3be6a35f run on my pod; public.bin equals pack_public of main's frozen fp8-hopper set, 0 mismatches. Merge rewrite: the same export with --no-merge reproduces byte for byte the unmerged statement verified for art:2e7baba7 (request 5), and my check with main's parse_circuit (23-lk-merge-check.py) finds the dumped circuit to be exactly its tag-merge: non-lookup lines identical, 139/139 queries = key + tag*2^20, bare tag constant, tag<->table bijective over 10 tables (ALIGN4 LEAD LEADNORM R6 R7 SHIFT SSHIFT_HI SSHIFT_LO TNORM T_OP); LK rows = the tagged union of the 10 source tables as a multiset (261968 = 261968), first column unique and < P. Negatives, all rejected: mutate --sample 64 (356/356), my public word +1 at VU 17, the producer's 4 LK-aimed negatives (r6_key, shift_out, t_op_out, tnorm_out: 'LogUp LK level 0: final check') and word_plus / word_minus / sign_flip / exp_plus (art:70bbba68) with my binary; its honest case accepted." \
  --seconds 1.17 \
  $O/verify.out $O/statement-check.json $O/lk-merge-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/mutate.log $O/neg-mine.log \
  $O/negp-r6_key.log $O/negp-shift_out.log $O/negp-t_op_out.log $O/negp-tnorm_out.log $O/negp-honest.log
