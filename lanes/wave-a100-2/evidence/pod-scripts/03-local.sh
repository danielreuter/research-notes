#!/usr/bin/env bash
# wave-a100-2 extra local cells (depth checks, committed column).
#   03-local.sh ROUND SPEC...     SPEC = tag:relation:batch:depth[:extra args, comma-separated]; order reversed on even rounds.
# committed column: shared64:bf16-ampere:16384:4:--auth,included-hash-shared,--tile,64x64
source /workspace/wave-a100/pod-scripts/lib.sh
r=$1; shift
S=("$@")
if [ $((r % 2)) -eq 0 ]; then R=(); for ((i=${#S[@]}-1; i>=0; i--)); do R+=("${S[$i]}"); done; S=("${R[@]}"); fi
for spec in "${S[@]}"; do
  IFS=: read tag rel batch depth extra <<< "$spec"
  b $tag-r$r $rel $batch $depth local ${extra//,/ }
done
echo "$(date -u +%H:%M:%S) LOCAL_ROUND_${r}_DONE $*" | tee -a $SUM
