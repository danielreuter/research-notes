#!/bin/bash
# vyv-rf-c1-big, second gate (b) at the lane head after the test-only module move: the lints and gate (b) (xdist) at head, each in its
# own copy of /workspace/head; the base run of big_gate_b.sh (same pod, same flags) is the comparison.   logs: /workspace/c1/logs/ -> $RESEARCH_RUN_DIR/c1-logs/
set -u
L=/workspace/c1/logs; mkdir -p $L
finish() { mkdir -p $RESEARCH_RUN_DIR/c1-logs; cp -a $L/. $RESEARCH_RUN_DIR/c1-logs/; echo "GATE-B2-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK"; exit 3; }
rm -rf /workspace/head2-l /workspace/head2-b; cp -a /workspace/head /workspace/head2-l; cp -a /workspace/head /workspace/head2-b
bash /workspace/c1/lints.sh /workspace/head2-l lints-head2
export OMP_NUM_THREADS=3
bash /workspace/c1/gate_b.sh /workspace/head2-b gate_b-xdist-head2 -n 12 --dist loadfile
echo "head2: $(tail -2 $L/gate_b-xdist-head2.log | head -1)"
