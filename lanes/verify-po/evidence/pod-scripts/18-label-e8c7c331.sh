#!/usr/bin/env bash
# verify-po: label the SP1 A100 BF16 sec134 (D2) result art:e8c7c331 (evidence from 15-sp1-verify.sh, run r20260924-224326-a84c;
# host built by 17-sp1-sec134-build.sh, run r20260924-223547-6b33).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
O=/workspace/verify-po/sp1-e8c7c331
$PY $RESEARCH_RUN_DIR/inputs/11-label.py art:e8c7c331bd0cb15ea021111403ce7f13cbb9e7d71e2204120c46a5ce6ed4d733 \
  --tree art:e31556f58498a4669d3482d5180c242ad36f20f634bdb40b09a73e170fc6cc4d \
  --verifier "veritor-zk-host relation-bare sec134 CPU verifier (backends/sp1 @ main ab9573fd, --locked; sp1-primitives 6.6.0 fri_params.rs core queries 124->175 via lane/sp1-128 d1111579 sec128/build.sh VERIFIER_ONLY=1) built on pod vy-verify-po; sha256 ad6ec855 (byte-identical to the producer's), ELF f11cf2cc, vk 0x00dfced1" \
  --detail "5/5 core proofs (run-files art:e31556f5 proofs/proof-rep{0..4}.bin) accepted: ok, verdict, statement_match true, unsound false, vk 0x00dfced1, statement_digest 5e0dd245; verify 2.13-2.15 s each (~38 s per process incl. setup). Statement written by me from main's frozen bf16-ampere set (vu-k1536, manifest 059103cf), byte-identical to the dump's statement.bin. Negatives, all rejected: last y byte flipped (statement_match false); the STOCK host built from main (124 queries, sha256 06e0d736) on rep0 (ok false). D2 drill-down row; Table 2 still rejects it on security.achieved_log2 -95.461 by design." \
  --seconds 2.15 \
  $O/verify.out /workspace/verify-po/sp1/build-sec134.out
