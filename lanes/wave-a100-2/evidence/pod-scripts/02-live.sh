#!/usr/bin/env bash
# wave-a100-2 live rounds: same-DC verifier vy-wave-a100-verifier (EU-RO-1) at tcp://193.183.22.53:1823.
#   02-live.sh ROUND SPEC...      SPEC = tag:relation:batch:depth[:extra args, comma-separated]; order reversed on even rounds.
# -> runs/live-<tag>-r<ROUND>/ (t.total_live + net.* + the session verdict), 3 reps, rep 1 dumped.
source /workspace/wave-a100/pod-scripts/lib.sh
export VERIFIER_URL=${VERIFIER_URL:-tcp://193.183.22.53:1823}
r=$1; shift
S=("$@")
if [ $((r % 2)) -eq 0 ]; then R=(); for ((i=${#S[@]}-1; i>=0; i--)); do R+=("${S[$i]}"); done; S=("${R[@]}"); fi
for spec in "${S[@]}"; do
  IFS=: read tag rel batch depth extra <<< "$spec"
  b live-$tag-r$r $rel $batch $depth live ${extra//,/ }
done
echo "$(date -u +%H:%M:%S) LIVE_ROUND_${r}_DONE" | tee -a $SUM
