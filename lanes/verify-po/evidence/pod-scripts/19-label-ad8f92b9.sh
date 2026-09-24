#!/usr/bin/env bash
# verify-po: label the A-GKR RTX 5090 NVFP4 result art:ad8f92b9 (agkr-nvf4 handoff 20260924T2305Z; evidence from
# 10-agkr-nvf4-verify.sh PREV=ab57df0a, run r20260924-231454-fa00).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-ad8f92b9
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:ad8f92b9e1badc22fda51b004e8f1458d0d4aca6d89e1630ace2df5a68e105f2 \
  --tree art:82f70cb91d66d39118cc46a03a4a4cb7dfd3ac6190ed8770d057a90f9f9a4315 \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ lane/agkr-nvf4 3c769c6d, byte-identical to ab57df0a's (diff -r on my pod); = main ab9573fd + the optional multi-column 'public' line, diff reviewed by verify-po; binary sha256 f271e4221a7520d4), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "3/3 proofs (run-files art:82f70cb9 proofs/rep{0,1,2}.bin, sha256 b6cf5f09...) accepted: vus 4096, units 98304, steps 24, slots 976, msgs 2694, bytes_read 9491200, ligero_rows 11666, committed_elements 47782943; 0.74-0.99 s at 15 threads (16 vCPU EPYC 9754). Statement: circuit.txt (485 columns, depth 1, tables E2M1X2 + merged LK) / epilogue.txt / chain.txt ('public s t f') and manifest byte-identical to lane/agkr-nvf4@ab57df0a's 'gpu.nvf4.circuit export' run on my pod (main has no NVFP4 A-GKR circuit); public.bin (4096 x 3) equals (sign, exponent field, fraction) of the final FP32 word of main ab9573fd's fp4/chain.instances_fp4(4096) (digest d2d65f65...), 0 rows mismatched. The same binary accepts the fp8-ada y16 statement art:89a2ce85. Negatives, all rejected: mutate --sample 24 (148/148), my s flip (VU 5), t+1 (VU 17), f+1 (VU 4095), public line reordered, public line removed (parse error)." \
  --seconds 0.99 \
  $O/verify.out $O/statement-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/mutate.log $O/regress_fp8.json \
  $O/neg-s_flip.log $O/neg-t_plus.log $O/neg-f_plus.log $O/neg-public_reordered.log $O/neg-no_public_line.log
