#!/bin/bash
# The two B=1 T1 replay_partition checks (rows #11, #39), side by side, each in its own gate (a) process (gate_a.sh: T0,T1, no key), with
# each process's peak RSS sampled every 5 s.  One runner at a time (flock).
#   usage: run_big.sh TREE      logs: /workspace/out/gates/big_r{11,39}.{log,xml,status,rss}, big.DONE
T=$1; L=/workspace/out/gates
exec 9>$L/big.lock
flock -n 9 || { echo "run_big.sh is already running" >&2; exit 1; }
watch_rss() {  # PID TAG: peak RSS of the pytest child of gate_a.sh PID
  local peak=0 kb
  while kill -0 $1 2>/dev/null; do
    kb=$(ps --ppid $1 -o rss= 2>/dev/null | awk '{s+=$1} END {print s+0}')
    [ "$kb" -gt "$peak" ] && peak=$kb && echo "$(date -u +%FT%TZ) peak_rss_gb $((peak / 1048576))" > $L/$2.rss
    sleep 5
  done
}
pids=()
for r in 11 39; do
  /workspace/rff24/gate_a.sh "$T" big_r$r -k "replay_partition and r$r" &
  p=$!; pids+=($p); watch_rss $p big_r$r &
done
wait "${pids[@]}"
wait
echo "done $(date -u +%FT%TZ)" > $L/big.DONE
