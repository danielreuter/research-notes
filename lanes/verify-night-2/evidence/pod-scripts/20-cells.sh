#!/usr/bin/env bash
# verify-night-2: one group of B-Ligero included-hash results over one N: 05 negatives on each run-files tree (NEG=0 reuses
# an earlier summary), then 16 (reverify + 04 binding + 06 R1/R2/R4 core roots) with LABEL only if every tree's negatives
# came out right.  Frees each tree's fetched copy after use (the 16384-VU blake3 tree is 5.4 GB).
#   TAG=t VN2_N=n LABEL=0|1 NEG=0|1 PV_NOTE="..." bash 20-cells.sh TREE... -- RESULT...
set -uo pipefail
I=$RESEARCH_RUN_DIR/inputs; W=/workspace/verify-night-2; TAG=${TAG:?}; N=${VN2_N:-4096}
trees=(); while [ "$1" != "--" ]; do trees+=("$1"); shift; done; shift
for t in "${trees[@]}"; do
  s=$W/neg-$TAG-${t:4:8}/summary.txt
  if [ "${NEG:-1}" = 1 ]; then
    echo "=== [$(date -u +%H:%M:%S)] negatives $t"; bash $I/05-negatives.sh $t $TAG-${t:4:8}
  else
    echo "=== negatives $t: reusing $s"
  fi
  cat $s
done
negok=1
for t in "${trees[@]}"; do
  s=$W/neg-$TAG-${t:4:8}/summary.txt
  grep -q '^base: .*batch_accepted=True' $s && [ $(grep -cE '^(proofbyte|stmtbyte|swapstmt): .*batch_accepted=False' $s) = 3 ] || negok=0
done
echo "negatives ok=$negok"; df -h /workspace | tail -1
lab=${LABEL:-0}; [ $negok = 1 ] || lab=0
TAG=$TAG LABEL=$lab VN2_N=$N VN2_NOTE="${PV_NOTE:-}" bash $I/16-sh-recheck.sh "$@" | grep -vE '^\s*$'
rm -rf $W/$TAG/rv
echo "=== [$(date -u +%H:%M:%S)] 20 done ($TAG)"
