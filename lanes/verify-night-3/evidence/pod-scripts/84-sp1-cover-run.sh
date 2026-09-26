#!/usr/bin/env bash
# verify-night-3: the #101 sampled-cover verification (after 80-sp1-setup.sh). usage: 84-sp1-cover-run.sh SNAPSHOT_ART
set -uo pipefail
S=$(pwd)
source "$(dirname "$0")/lib.sh"
cd $S
export VERITY_SP1_HOST=/workspace/bin/veritor-zk-host-cpu
export PYTHONPATH="$S/packages/verity/src:$S/backends/sp1/python:$S/backends/numerical/python:$S/integrations/vllm:$S/tools/research/src:$S"
O=$RESEARCH_RUN_DIR/out; mkdir -p $O
sha256sum $VERITY_SP1_HOST | tee $O/host.sha256; $VERITY_SP1_HOST info | tail -1 | tee $O/host-info.json
$PY "$(dirname "$0")/83-sp1-cover-verify.py" $W/cover "$1" 2>&1 | tee $O/verify.log
rc=${PIPESTATUS[0]}
cp $W/cover/cover-verdict*.json $W/cover/my-prep-*.log $O/ 2>/dev/null
exit $rc
