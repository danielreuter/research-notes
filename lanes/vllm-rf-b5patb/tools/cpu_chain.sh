#!/bin/bash
# cpu pod: lints at head and base, then gate (b) at head, then at base, sequentially on one pod.
#   usage: cpu_chain.sh HEAD_TREE BASE_TREE
H=$1; B=$2
bash /workspace/b5pat/lints.sh "$H" lints_head; echo "lints_head rc=$?"
bash /workspace/b5pat/lints.sh "$B" lints_base; echo "lints_base rc=$?"
bash /workspace/b5pat/gate_b.sh "$H" b_head; echo "b_head rc=$?"
bash /workspace/b5pat/gate_b.sh "$B" b_base; echo "b_base rc=$?"
echo "chain done $(date -u +%FT%TZ)"
