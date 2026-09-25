#!/bin/bash
# vyv-rf-c1-big: the lints at head and at base, then gate (b) (xdist, a1's mode) at head and at base at the same time, each in its own
# copy of its tree.   logs: /workspace/c1/logs/ -> $RESEARCH_RUN_DIR/c1-logs/
set -u
L=/workspace/c1/logs; mkdir -p $L
finish() { mkdir -p $RESEARCH_RUN_DIR/c1-logs; cp -a $L/. $RESEARCH_RUN_DIR/c1-logs/; echo "GATE-B-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK"; exit 3; }
for t in head base; do rm -rf /workspace/$t-l /workspace/$t-b; cp -a /workspace/$t /workspace/$t-l; cp -a /workspace/$t /workspace/$t-b; done
bash /workspace/c1/lints.sh /workspace/head-l lints-head
bash /workspace/c1/lints.sh /workspace/base-l lints-base
export OMP_NUM_THREADS=3
bash /workspace/c1/gate_b.sh /workspace/head-b gate_b-xdist-head -n 12 --dist loadfile &
P1=$!
bash /workspace/c1/gate_b.sh /workspace/base-b gate_b-xdist-base -n 12 --dist loadfile &
P2=$!
wait $P1 $P2
for t in head base; do echo "$t: $(tail -2 $L/gate_b-xdist-$t.log | head -1)"; done
