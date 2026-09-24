#!/usr/bin/env bash
# wave-4090: column 2 (committed: --auth included-hash-shared --tile 64x64, fp8-ada v1, l=16384 p4) in 3 rounds, then the
# drill-downs +hash (unshared Poseidon2), +ajtai-n64, +blake3 (l=4096) one round each. Local (rep1 dumped) then live per cell.
# Usage: PARTS="shared hash ajtai blake3" bash 20-committed-drill.sh
source /workspace/wave-4090/scripts/lib.sh
for part in ${PARTS:-shared hash ajtai blake3}; do
  case $part in
    shared) for r in ${SHARED_ROUNDS:-1 2 3}; do
              for m in local live; do run shared-p4-r$r-$m $m fp8-ada 16384 4 5 --auth included-hash-shared --tile 64x64; done
            done ;;
    hash)   for m in local live; do run hash-p4-$m $m fp8-ada 16384 4 5 --auth included-hash; done ;;
    ajtai)  for m in local live; do run ajtai-n64-p4-$m $m fp8-ada 16384 4 5 --auth included-hash --leaf ajtai-n64; done ;;
    blake3) for m in local live; do run blake3-l4096-p${B3P:-2}-$m $m fp8-ada 4096 ${B3P:-2} 3 --auth included-hash --leaf blake3; done ;;
  esac
done
echo "COMMITTED_DRILL_DONE ${PARTS:-shared hash ajtai blake3}" | tee -a $LOG
