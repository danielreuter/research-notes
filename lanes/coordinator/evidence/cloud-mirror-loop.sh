#!/usr/bin/env bash
# the cloud-lane mirror loop: one pass (pass.sh) about every 5 min, measured from each pass's start
S=/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lanes/coordinator/evidence
while :; do
  t0=$(date +%s)
  timeout 540 bash ~/cloud-mirror/pass.sh 2>&1 | grep -v setlocale >> /tmp/cloud-mirror.log
  [ "${PIPESTATUS[0]}" = 124 ] && echo "$(date -u +%H:%MZ) TIMEOUT pass killed after 540 s" >> /tmp/cloud-mirror.log
  cp ~/cloud-mirror/pass.sh $S/cloud-mirror-control-pod.sh 2>/dev/null; cp ~/cloud-mirror/loop.sh $S/cloud-mirror-loop.sh 2>/dev/null
  left=$(( 300 - ($(date +%s) - t0) )); [ $left -gt 0 ] && sleep $left
done
