#!/bin/bash
# vyv-rf-c1-big: gate (a) T0+T1 at the lane head after the test-only module move, in its own copy of /workspace/head, from the
# fixtures big_gate_a.sh prefetched into the pod store (no key on the pod).   logs: /workspace/c1/logs/ -> $RESEARCH_RUN_DIR/c1-logs/
set -u
L=/workspace/c1/logs; mkdir -p $L
finish() { mkdir -p $RESEARCH_RUN_DIR/c1-logs; cp -a $L/. $RESEARCH_RUN_DIR/c1-logs/; echo "GATE-A2-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK"; exit 3; }
grep -q 'fail=0 key_deleted=yes' $L/prefetch.log || { echo "prefetch incomplete"; exit 5; }
[ -e /root/r2ro.env ] && { echo "refusing: /root/r2ro.env present"; exit 4; }
rm -rf /workspace/head2-a; cp -a /workspace/head /workspace/head2-a
( while sleep 30; do echo "$(date -u +%FT%TZ) $(cat /sys/fs/cgroup/memory.current 2>/dev/null) $(ps -eo rss= | sort -n | tail -1)"; done ) > $L/gate_a2.rss 2>&1 &
MON=$!
bash /workspace/c1/gate_a.sh /workspace/head2-a gate_a-t0t1-head2
kill $MON 2>/dev/null
tail -3 $L/gate_a-t0t1-head2.log
