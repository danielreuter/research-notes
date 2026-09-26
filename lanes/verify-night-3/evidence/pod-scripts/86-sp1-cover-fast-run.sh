#!/usr/bin/env bash
# verify-night-3: 85-sp1-cover-fast.py over "ART,PREP_DIR,PROD_DIR" triples (rebuilds from earlier runs on this pod)
set -uo pipefail
S=$(pwd)
source "$(dirname "$0")/lib.sh"
cd $S
export VERITY_SP1_HOST=/workspace/bin/veritor-zk-host-cpu
export PYTHONPATH="$S/packages/verity/src:$S/backends/sp1/python:$S/backends/numerical/python:$S/tools/research/src:$S"
O=$RESEARCH_RUN_DIR/out; mkdir -p $O; rc=0
$VERITY_SP1_HOST info | tail -1 | tee $O/host-info.json
for t in "$@"; do IFS=, read A P D <<< "$t"
  $PY "$(dirname "$0")/85-sp1-cover-fast.py" $W/fast $A $P $D 2>&1 | tee -a $O/verify.log; [ ${PIPESTATUS[0]} = 0 ] || rc=1
  cp $P/meta.json $O/my-meta-${A:4:8}.json
done
cp $W/fast/cover-verdict*.json $O/ 2>/dev/null
exit $rc
