#!/bin/bash
# vyv-rf-c1-big, gate (b) (xdist) at the lane head 53314d1c in its own copy of /workspace/head; the base run of big_gate_b.sh (same pod,
# same flags) is the comparison.   logs: /workspace/c1/logs/ -> $RESEARCH_RUN_DIR/c1-logs/
set -u
L=/workspace/c1/logs; mkdir -p $L
finish() { mkdir -p $RESEARCH_RUN_DIR/c1-logs; cp -a $L/gate_b-xdist-head3.* $RESEARCH_RUN_DIR/c1-logs/; echo "GATE-B3-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
grep -q '"commit": "53314d1c' /workspace/head/.research-source.json || { echo "head is not 53314d1c"; exit 3; }
rm -rf /workspace/head3-b; cp -a /workspace/head /workspace/head3-b
export OMP_NUM_THREADS=3
bash /workspace/c1/gate_b.sh /workspace/head3-b gate_b-xdist-head3 -n 12 --dist loadfile
echo "head3: $(tail -2 $L/gate_b-xdist-head3.log | head -1)"
