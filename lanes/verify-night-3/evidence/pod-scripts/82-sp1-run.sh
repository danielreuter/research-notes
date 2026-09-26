#!/usr/bin/env bash
# verify-night-3: SP1 below-bar verification run (after 80-sp1-setup.sh). usage: 82-sp1-run.sh ART...
set -uo pipefail
S=$(pwd)
source "$(dirname "$0")/lib.sh"
cd $S
export VERITY_SP1_HOST=/workspace/bin/veritor-zk-host-cpu
export PYTHONPATH="$S/packages/verity/src:$S/backends/sp1/python:$S/backends/numerical/python:$S/integrations/vllm:$S/tools/research/src:$S"
O=$RESEARCH_RUN_DIR/out; mkdir -p $O
sha256sum $VERITY_SP1_HOST | tee $O/host.sha256; $VERITY_SP1_HOST info | tail -1 | tee $O/host-info.json
$PY "$(dirname "$0")/81-sp1-verify.py" $W/sp1 "$@" 2>&1 | tee $O/verify.log
rc=${PIPESTATUS[0]}
cp $W/sp1/verdict*.json $W/sp1/prep-*.log $O/ 2>/dev/null
for d in $W/sp1/prep-*; do [ -d $d ] && cp $d/meta.json $O/$(basename $d)-meta.json; done
exit $rc
