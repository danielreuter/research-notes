#!/bin/bash
# gate (a) T0+T1's two B=1 checks, deselected on the 64 GB pod, at head, side by side: one gate_a_t01.sh per check (-k), own tree copy and
# scratch each.  Memory sampled every 15 s -> logs/big.rss.
#   usage: run_big.sh [TREE [TAGPREFIX]]      logs: /workspace/rff3/logs/<TAGPREFIX>_r{11,39}.{log,xml,env,out}
T=${1:-/workspace/head}; P=${2:-big}
cd /workspace/rff3 || exit 3
mem() { if [ -f /sys/fs/cgroup/memory.current ]; then echo "cg=$(( $(cat /sys/fs/cgroup/memory.current) / 1073741824 ))G"
        else echo "cg=$(( $(cat /sys/fs/cgroup/memory/memory.usage_in_bytes) / 1073741824 ))G"; fi; }
peak() { if [ -f /sys/fs/cgroup/memory.peak ]; then echo "$(( $(cat /sys/fs/cgroup/memory.peak) / 1073741824 ))G"
         else echo "$(( $(cat /sys/fs/cgroup/memory/memory.max_usage_in_bytes) / 1073741824 ))G"; fi; }
PIDS=()
for r in r11 r39; do
  C=$T-$r; [ -d "$C" ] || cp -a "$T" "$C"
  setsid nohup nice ./gate_a_t01.sh "$C" ${P}_$r -k "T1-replay_partition-$r" > logs/${P}_$r.out 2>&1 < /dev/null &
  PIDS+=($!)
done
echo "started $(date -u +%FT%TZ) pids ${PIDS[*]}" >> logs/$P.rss
alive() { for p in "${PIDS[@]}"; do kill -0 "$p" 2>/dev/null && return 0; done; return 1; }
while alive; do
  echo "$(date -u +%T) $(mem) $(ps -eo rss=,args= | awk '$2 ~ /python/ && $0 ~ /pytest/ {printf "%dG ", $1/1048576}')" >> logs/$P.rss; sleep 15
done
wait
echo "done $(date -u +%FT%TZ) peak=$(peak)" >> logs/$P.rss
touch logs/$P.DONE
