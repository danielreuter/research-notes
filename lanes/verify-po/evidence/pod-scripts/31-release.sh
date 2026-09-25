#!/usr/bin/env bash
# verify-po: the coordinator's "release" of held A-GKR labels (hold 20260925T0050Z). Writes verified=accepted --by verify-po
# from each already-registered verdict; no new verdict.  RELEASE="45c5be4a 3ae971dd ad76c106 dfbc86c4 53a64e8b f277786d" (any subset).
set -uo pipefail
declare -A SCRIPT=([45c5be4a]=25-verdict-45c5be4a.sh [dfbc86c4]=28-verdict-dfbc86c4.sh [3ae971dd]=29-verdict-3ae971dd.sh [53a64e8b]=30-verdict-53a64e8b.sh
                   [ad76c106]=34-verdict-ad76c106.sh [f277786d]=36-verdict-f277786d.sh)
declare -A VIDS=(
  [45c5be4a]=art:df4d2c3c08b423132ea331409ab12b3ef59acef922c66e6f15e7b608d694d8ee
  [dfbc86c4]=art:7d3aaf2e00a74d9f90495735bc9e945d8806a0e811d90464613fe3e1178c0954
  [3ae971dd]=art:e96f50acd4beda49505200790eb9d80aec4d645427da1a02aa6ad74ac21f8c01
  [53a64e8b]=art:223c8efe0d2c44e723ffead78eeee5ef85af562fa3338ce8e490db358a3d81c3
  [ad76c106]=art:b86ca2a86f836be072db40208da679c76e48b6006bde3c0067a43798987ebe5f
  [f277786d]=art:4513180dba816a911ba1d57ddf5b6e5fd956dd40d698ca10e9c080e982ef56b5)
for t in $RELEASE; do
  echo "=== release $t from ${VIDS[$t]}"
  HOLD=0 VID=${VIDS[$t]} bash $RESEARCH_RUN_DIR/inputs/${SCRIPT[$t]}; echo "$t rc=$?"
done
