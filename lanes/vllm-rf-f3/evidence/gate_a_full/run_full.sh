#!/bin/bash
# gate (a) T0+T1 IN FULL (nothing deselected) at head and at base side by side on the 512 GB pod: one gate_a_t01.sh per tree, each in a
# fresh copy of its tree (the suite writes under the tree) with its own scratch.  Memory sampled every 30 s -> logs/full.rss.
#   usage: run_full.sh      logs: /workspace/rff3/logs/full_{head,base}.{log,xml,env,out}, logs/full.rss, logs/full.DONE
cd /workspace/rff3 || exit 3
[ -f /root/r2ro.env ] && { echo "key still on disk: refusing"; exit 3; }
mem() { if [ -f /sys/fs/cgroup/memory.current ]; then echo "cg=$(( $(cat /sys/fs/cgroup/memory.current) / 1073741824 ))G"
        else echo "cg=$(( $(cat /sys/fs/cgroup/memory/memory.usage_in_bytes) / 1073741824 ))G"; fi; }
peak() { if [ -f /sys/fs/cgroup/memory.peak ]; then echo "$(( $(cat /sys/fs/cgroup/memory.peak) / 1073741824 ))G"
         else echo "$(( $(cat /sys/fs/cgroup/memory/memory.max_usage_in_bytes) / 1073741824 ))G"; fi; }
PIDS=()
for pair in head:/workspace/head base:/workspace/basetree; do
  TAG=${pair%%:*}; T=${pair#*:}; C=$T-reg
  rm -rf "$C"; cp -a "$T" "$C"
  setsid nohup nice ./gate_a_t01.sh "$C" full_$TAG > logs/full_$TAG.out 2>&1 < /dev/null &
  PIDS+=($!)
done
echo "started $(date -u +%FT%TZ) pids ${PIDS[*]}" >> logs/full.rss
alive() { for p in "${PIDS[@]}"; do kill -0 "$p" 2>/dev/null && return 0; done; return 1; }
while alive; do
  echo "$(date -u +%T) $(mem) $(ps -eo rss=,args= | awk '$2 ~ /python/ && $0 ~ /pytest/ {printf "%dG ", $1/1048576}')" >> logs/full.rss; sleep 30
done
wait
echo "done $(date -u +%FT%TZ) peak=$(peak)" >> logs/full.rss
touch logs/full.DONE
