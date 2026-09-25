#!/usr/bin/env bash
# verify-po: verdict for the A-GKR RTX 5090 NVFP4 result art:f277786d (agkr-nvf4 handoff 20260925T0210Z; same statement and proof
# bytes as art:dfbc86c4; evidence from 35-agkr-nvf4-f277786d.sh). HOLD=1 (default): verdict only (coordinator 20260925T0050Z);
# HOLD=0 VID=art:<verdict>: the release.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/agkr-f277786d
if [ "${HOLD:-1}" = 1 ]; then MODE=(--hold); else MODE=(--vid "$VID"); fi
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:f277786dadaebbffc3fe01f02e0d49452a7dfc5fceed359cb746588b79eac63c "${MODE[@]}" \
  --tree art:1f0b0b60645c02e158c1c8fda975ad04e76e3e18782ee92ee8c26a7247941cad \
  --verifier "verity-gkr-verify (backends/gkr/verifier @ lane/agkr-nvf4 3c769c6d, byte-identical to c97d2ad2's (diff -r on my pod); = main ab9573fd + the optional multi-column 'public' line, diff reviewed by verify-po; binary sha256 f271e4221a7520d4), cargo --release + cargo test (8/8) on pod vy-verify-po, --threads 15" \
  --detail "5/5 proofs (run-files art:1f0b0b60 proofs/rep{0..4}.bin, sha256 ebe7c545..., byte-identical to art:dfbc86c4's run-files art:50f4fe91, as are all statement files) accepted: vus 4096, units 98304, steps 24; 0.47-0.53 s at 15 threads. Statement: circuit.txt (485 columns, 700 wires, depth 1, 166 queries into one table LK 5 x 110613) / epilogue.txt / chain.txt and manifest byte-identical to lane/agkr-nvf4@c97d2ad2's 'gpu.nvf4.circuit export' run on my pod; public.bin (4096 x 3) equals (s, t, f) of main ab9573fd's fp4/chain.instances_fp4(4096), 0 rows mismatched. Rewrites (BOOL_QUADRATIC, PAIRED) checked with main's parse_circuit against the 2b25df7f circuit verified for art:5adf62eb (27-nvf4-rewrite-check.py): the same 226 lookup facts per unit, ok. Negatives, all rejected: mutate --sample 24 (148/148), my s flip (VU 5), t+1 (VU 17), f+1 (VU 4095), public line reordered, public line removed (parse error)." \
  --seconds 0.53 \
  $O/verify.out $O/statement-check.json $O/rewrite-check.json $O/out_rep0.json $O/out_rep1.json $O/out_rep2.json $O/out_rep3.json $O/out_rep4.json \
  $O/mutate.log $O/neg-s_flip.log $O/neg-t_plus.log $O/neg-f_plus.log $O/neg-public_reordered.log $O/neg-no_public_line.log
