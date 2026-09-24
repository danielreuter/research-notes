#!/usr/bin/env bash
# wave-4090-2: run named cells in order, one heavy job at a time (lib.sh `run`: waits for an empty GPU; local dumps rep 1,
# live uses $VERIFIER). Outputs /workspace/wave-4090/runs/<tag>, one summary line per run in /workspace/wave-4090/runs.txt.
# Usage: CELLS="shared-r1 shared-r2 ..." MODES="local live" bash 30-cells.sh
#   bare-v3x4-p8-rN / bare-v3x4-p4-rN : bare headline candidates (live rounds; local rounds were done by wave-4090)
#   shared-rN : committed column (--auth included-hash-shared --tile 64x64), fp8-ada v1 l=16384 p4
#   hash / ajtai / blake3 : drill-downs (unshared Poseidon2, Ajtai n64 leaf, BLAKE3 leaf l=4096 p2)
source /workspace/wave-4090/scripts/lib.sh
for c in $CELLS; do
  for m in ${MODES:-local live}; do
    case $c in
      bare-v3x4-p8-r*) run $c-$m $m fp8-ada-v3x4 4096 8 5 ;;
      bare-v3x4-p4-r*) run $c-$m $m fp8-ada-v3x4 4096 4 5 ;;
      bare-v3-p4-r*)   run $c-$m $m fp8-ada-v3 16384 4 5 ;;
      bare-v1-p4-r*)   run $c-$m $m fp8-ada 16384 4 5 ;;
      shared-r*)       run shared-p4-${c#shared-}-$m $m fp8-ada 16384 4 5 --auth included-hash-shared --tile 64x64 ;;
      hash)            run hash-p4-$m $m fp8-ada 16384 4 5 --auth included-hash ;;
      ajtai)           run ajtai-n64-p4-$m $m fp8-ada 16384 4 5 --auth included-hash --leaf ajtai-n64 ;;
      blake3)          run blake3-l4096-p2-$m $m fp8-ada 4096 2 3 --auth included-hash --leaf blake3 ;;
      *) echo "unknown cell $c" | tee -a $LOG ;;
    esac
  done
done
echo "CELLS_DONE $CELLS / ${MODES:-local live}" | tee -a $LOG
