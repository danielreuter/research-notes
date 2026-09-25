#!/bin/bash
# Coordinator disk watch (v3, 14:15Z): every 8 min, log free space on the data volume. Under 1.0 GiB, log an URGENT line and
# drop a handoff in lanes/coordinator/ (at most once an hour); the coordinator then stops laptop-side work and tells the root.
# Run from a stable directory: cd ~ && nohup bash .../disk-watch.sh &
set -u
E=~/.research/notes/lanes/coordinator/evidence
LOG=$E/disk-watch.log
last=0
while true; do
  kb=$(df -k /System/Volumes/Data | awk 'NR==2 {print $4}')
  gib=$(awk -v k="$kb" 'BEGIN {printf "%.2f", k / 1048576}')
  echo "$(date -u +%FT%TZ) free ${gib} GiB" >> "$LOG"
  if awk -v g="$gib" 'BEGIN {exit !(g < 1.0)}'; then
    echo "$(date -u +%FT%TZ) URGENT under 1.0 GiB" >> "$LOG"
    now=$(date +%s)
    if [ $((now - last)) -ge 3600 ]; then
      T=$(date -u +%Y%m%dT%H%MZ)
      printf '# URGENT: laptop disk %s GiB free (< 1.0 GiB rule)\n\nStop laptop-side work and fetches; evict R2-verified run files; tell the root.\n' "$gib" \
        > ~/.research/notes/lanes/coordinator/$T-handoff-from-disk-watch.md
      last=$now
    fi
  fi
  sleep 480
done
