#!/usr/bin/env bash
# verify-po: agkr-nvf4 handoff 20260925T0210Z, A-GKR RTX 5090 NVFP4 art:f277786d (c97d2ad2; same statement and proof bytes as
# art:dfbc86c4 / art:53a64e8b). 10-agkr-nvf4-verify.sh PREV=c97d2ad2, 27-nvf4-rewrite-check.py vs the 2b25df7f circuit, and cmp
# of every file with art:dfbc86c4's verified tree.
set -uo pipefail
export TREE=art:1f0b0b60645c02e158c1c8fda975ad04e76e3e18782ee92ee8c26a7247941cad TAG=f277786d PREV=c97d2ad2
bash $RESEARCH_RUN_DIR/inputs/10-agkr-nvf4-verify.sh
source /workspace/env.sh
O=/workspace/verify-po/agkr-$TAG
echo "=== rewrite check vs 2b25df7f"
PYTHONPATH=/workspace/src/backends/gkr:/workspace/src $PY $RESEARCH_RUN_DIR/inputs/27-nvf4-rewrite-check.py \
  /workspace/verify-po/agkr-5adf62eb/tree/statement/circuit.txt $O/tree/statement/circuit.txt > $O/rewrite-check.json 2> $O/rewrite-check.err
echo "rewrite rc=$?"; grep -E '"(facts_equal|ok)"' $O/rewrite-check.json
echo "=== vs dfbc86c4 files"
for f in $(cd $O/tree && find proofs statement -type f | sort); do
  cmp -s $O/tree/$f /workspace/verify-po/agkr-dfbc86c4/tree/$f && echo "$f same" || echo "$f DIFFERS"
done
