#!/bin/bash
# vyv-rf-c1-big, the lints at the lane head after the p09 allowlist shrink (53314d1c: one JSON line removed, nothing else), in a copy of
# /workspace/head; gate (b) and gate (a) at 7218ffbb stand for the code.   logs: /workspace/c1/logs/ -> $RESEARCH_RUN_DIR/c1-logs/
set -u
L=/workspace/c1/logs; mkdir -p $L
finish() { mkdir -p $RESEARCH_RUN_DIR/c1-logs; cp -a $L/lints-head3.* $RESEARCH_RUN_DIR/c1-logs/; echo "LINTS3-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
grep -q '"commit": "53314d1c' /workspace/head/.research-source.json || { echo "head is not 53314d1c"; cat /workspace/head/.research-source.json; exit 3; }
rm -rf /workspace/head3-l; cp -a /workspace/head /workspace/head3-l
bash /workspace/c1/lints.sh /workspace/head3-l lints-head3
