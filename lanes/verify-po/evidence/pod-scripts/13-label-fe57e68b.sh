#!/usr/bin/env bash
# verify-po: label the A-GKR RTX 5090 NVFP4 result art:fe57e68b (evidence from 10-agkr-nvf4-verify.sh, run r20260924-220116-78b9).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-fe57e68b
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:fe57e68ba4c8f5a75eb9b83eb9cb1bde4a7ce8a5ac6b8ab364518758d45019a8 \
  --tree art:30c5bdf77a9093a1d93c86b1f151ceb5ece632715bfa88a2e1c606f502760ae7 \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ lane/agkr-nvf4 3c769c6d = main ab9573fd + the optional multi-column 'public' line in chain.txt, diff reviewed by verify-po; binary sha256 f271e4221a7520d4), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "3/3 proofs (run-files art:30c5bdf7 proofs/rep{0,1,2}.bin, sha256 fec5fc23...) accepted: vus 4096, units 98304, steps 24, slots 4236, msgs 14418, bytes_read 8537632; 0.60-0.85 s at 15 threads. Statement: circuit.txt / epilogue.txt / chain.txt ('public s t f') and manifest byte-identical to lane/agkr-nvf4@3c769c6d's 'gpu.nvf4.circuit export' run on my pod (main has no NVFP4 A-GKR circuit); public.bin (4096 x 3) equals (sign, exponent field, fraction) of the final FP32 word of main ab9573fd's fp4/chain.instances_fp4(4096) (digest d2d65f65..., = the result's), 0 rows mismatched. The same binary accepts the fp8-ada y16 statement art:89a2ce85 (default public line unchanged). Negatives, all rejected: mutate --sample 24 (148/148), my s flip (VU 5), t+1 (VU 17), f+1 (VU 4095), public line reordered, public line removed (parse error)." \
  --seconds 0.85 \
  $O/verify.out $O/statement-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/mutate.log $O/regress_fp8.json \
  $O/neg-s_flip.log $O/neg-t_plus.log $O/neg-f_plus.log $O/neg-public_reordered.log $O/neg-no_public_line.log
