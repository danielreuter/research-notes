#!/usr/bin/env bash
# verify-po: agkr-fp8 handoff 20260925T0203Z, two H100 FP8 A-GKR cells proved by lane/agkr-fp8 a97576b5.
# 1. art:b0c27291 (unchanged statement): 08-agkr-verify.sh with EXPORT_ARGS=--no-merge (a97576b5's export merges by default);
#    files compared with art:2e7baba7's verified tree.
# 2. art:ad76c106 (merged LK, label held): 24-agkr-fp8-merged.sh; files compared with art:3ae971dd's verified tree.
set -uo pipefail
I=$RESEARCH_RUN_DIR/inputs
export TARGET=fp8-hopper-wgmma-draft/2026-09-22 MODEL=hopper_e4m3_wgmma_k32 PREV=a97576b5
same() {  # same <tag> <earlier tag>
  local a=/workspace/verify-po/agkr-$1/tree b=/workspace/verify-po/agkr-$2/tree
  for f in $(cd $a && find proofs statement -type f | sort); do cmp -s $a/$f $b/$f && echo "$f same as $2" || echo "$f DIFFERS from $2"; done
}
echo "##### art:b0c27291 (unchanged statement)"
TREE=art:25c57ccb8815d411bcb985633dbcbe75ed3e3bcc11bb2916c19e1f93970e5b83 TAG=b0c27291 EXPORT_ARGS=--no-merge \
  NEGTREE=art:07b5adb8048af142ebc2f809eb02cf853c53816824debe62f1a3b2276325b653 bash $I/08-agkr-verify.sh
same b0c27291 2e7baba7
echo "##### art:ad76c106 (merged LK)"
TREE=art:55eb421ddcb57aa7d8880822530126fcc3fc5e2eddaf0ca95cc09262a51b660e TAG=ad76c106 \
  NEGTREE=art:70bbba68931935ef16b4ce31b159cf868f7dfa82ec63aabf7c57fcae01c45ad2 OLDSTMT=/workspace/verify-po/agkr-2e7baba7/tree/statement \
  bash $I/24-agkr-fp8-merged.sh
same ad76c106 3ae971dd
echo "##### done"
