#!/usr/bin/env bash
# verify-po: label the A-GKR RTX 5090 NVFP4 result art:49757870 (agkr-nvf4 handoff 20260925T0005Z; evidence from
# 10-agkr-nvf4-verify.sh PREV=716ea008, run r20260925-001640-4f37).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-49757870
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:49757870c9720787072c8593cf8a448b59d0d35e34e0e1a2021a4020ab2c4f15 \
  --tree art:78b3aadf21aabd37f1b104e63dde7d7261266c753d17a27613a3d6bb8f3c9ca0 \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ lane/agkr-nvf4 3c769c6d, byte-identical to 716ea008's (diff -r on my pod); = main ab9573fd + the optional multi-column 'public' line, diff reviewed by verify-po; binary sha256 f271e4221a7520d4), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "5/5 proofs (run-files art:78b3aadf proofs/rep{0..4}.bin, all sha256 091fecad..., the same bytes as art:5adf62eb's) accepted: vus 4096, units 98304, steps 24, slots 700, msgs 1689, bytes_read 9467080, ligero_rows 11666, committed_elements 47782943; 0.66-0.81 s at 15 threads (16 vCPU EPYC 9754). Statement: circuit.txt (485 columns, depth 1, one table LK 89119 rows) / epilogue.txt / chain.txt ('public s t f') and manifest byte-identical to lane/agkr-nvf4@716ea008's 'gpu.nvf4.circuit export' run on my pod (main has no NVFP4 A-GKR circuit); public.bin (4096 x 3) equals (sign, exponent field, fraction) of the final FP32 word of main ab9573fd's fp4/chain.instances_fp4(4096), 0 rows mismatched. The same binary accepts the fp8-ada y16 statement art:89a2ce85. Negatives, all rejected: mutate --sample 24 (148/148), my s flip (VU 5), t+1 (VU 17), f+1 (VU 4095), public line reordered, public line removed (parse error)." \
  --seconds 0.81 \
  $O/verify.out $O/statement-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/out_rep3.json $O/out_rep4.json \
  $O/mutate.log $O/regress_fp8.json $O/neg-s_flip.log $O/neg-t_plus.log $O/neg-f_plus.log $O/neg-public_reordered.log $O/neg-no_public_line.log
