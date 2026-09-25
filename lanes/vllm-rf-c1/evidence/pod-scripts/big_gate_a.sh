#!/bin/bash
# vyv-rf-c1-big: prefetch every row's fixtures with the read-only key the laptop piped into /root/r2ro.env (prefetch.sh deletes it), then
# gate (a) T0+T1 at head in its own copy of the tree.   logs: /workspace/c1/logs/ -> $RESEARCH_RUN_DIR/c1-logs/
set -u
L=/workspace/c1/logs; mkdir -p $L
finish() { rm -f /root/r2ro.env; mkdir -p $RESEARCH_RUN_DIR/c1-logs; cp -a $L/. $RESEARCH_RUN_DIR/c1-logs/; echo "GATE-A-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK"; exit 3; }
[ -s /root/r2ro.env ] || { echo "no key in /root/r2ro.env"; exit 4; }
rm -rf /workspace/head-a; cp -a /workspace/head /workspace/head-a
bash /workspace/c1/prefetch.sh /workspace/head-a
tail -1 $L/prefetch.log
grep -q 'fail=0 key_deleted=yes' $L/prefetch.log || { echo "prefetch incomplete"; exit 5; }
( while sleep 30; do echo "$(date -u +%FT%TZ) $(cat /sys/fs/cgroup/memory.current 2>/dev/null) $(ps -eo rss= | sort -n | tail -1)"; done ) > $L/gate_a.rss 2>&1 &
MON=$!
bash /workspace/c1/gate_a.sh /workspace/head-a gate_a-t0t1-head
kill $MON 2>/dev/null
tail -3 $L/gate_a-t0t1-head.log
