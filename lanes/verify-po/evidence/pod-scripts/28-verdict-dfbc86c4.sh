#!/usr/bin/env bash
# verify-po: verdict for the A-GKR RTX 5090 NVFP4 BOOL_QUADRATIC + PAIRED result art:dfbc86c4 (agkr-nvf4 handoff 20260925T0100Z;
# evidence from 10-agkr-nvf4-verify.sh PREV=b7cec878, run r20260925-010734-e1f8, and 27-nvf4-rewrite-check.py, run
# r20260925-011927-349e). HOLD=1 (default): verdict only (coordinator 20260925T0050Z); HOLD=0 VID=art:<verdict>: the release.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-dfbc86c4
if [ "${HOLD:-1}" = 1 ]; then MODE=(--hold); else MODE=(--vid "$VID"); fi
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:dfbc86c4434000c61d3d6b991148c8e8e8e914dbbd6ef27093d0d4f47fcd6fe7 "${MODE[@]}" \
  --tree art:50f4fe91635eb7216786ead66759ab90fdb6c3197258d957d0a7698f31e93bd8 \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ lane/agkr-nvf4 3c769c6d, byte-identical to b7cec878's (diff -r on my pod); = main ab9573fd + the optional multi-column 'public' line, diff reviewed by verify-po; binary sha256 f271e4221a7520d4), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "5/5 proofs (run-files art:50f4fe91 proofs/rep{0..4}.bin, sha256 ebe7c545...) accepted: vus 4096, units 98304, steps 24; 0.62-1.39 s at 15 threads. Statement: circuit.txt (485 columns, 700 wires, depth 1, 166 queries into one table LK 5 x 110613) / epilogue.txt / chain.txt ('public s t f') and manifest byte-identical to lane/agkr-nvf4@b7cec878's 'gpu.nvf4.circuit export' run on my pod; public.bin (4096 x 3) equals (s, t, f) of main ab9573fd's fp4/chain.instances_fp4(4096), 0 rows mismatched. Rewrites (BOOL_QUADRATIC, PAIRED) checked with main's parse_circuit against the 2b25df7f circuit verified for art:5adf62eb (27-nvf4-rewrite-check.py): the same 226 lookup facts per unit (46 R1 lookups replaced by exactly 46 product wires e*e with asserts w - e = 0; PR3/5/6/7 blocks are exactly all (x + 2^b y, x, y), each PR query's key = x + 2^b y; the 6 listed blocks identical), columns equal, every old product and assert present. Negatives, all rejected: mutate --sample 24 (148/148), my s flip (VU 5), t+1 (VU 17), f+1 (VU 4095), public line reordered, public line removed (parse error); the fp8-ada y16 regression accepts." \
  --seconds 1.39 \
  $O/verify.out $O/statement-check.json $O/rewrite-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/out_rep3.json $O/out_rep4.json \
  $O/mutate.log $O/regress_fp8.json $O/neg-s_flip.log $O/neg-t_plus.log $O/neg-f_plus.log $O/neg-public_reordered.log $O/neg-no_public_line.log
