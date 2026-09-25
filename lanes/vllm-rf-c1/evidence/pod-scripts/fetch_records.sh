#!/bin/bash
# Fetch regression-row records into /workspace/c1/records-<row> with the lane's own read-only key, then delete the key.
# usage: fetch_records.sh <tree> <row>=<art> ...
set -u
tree=$1; shift
cd "$tree"
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src
set -a; . /root/r2ro.env; set +a
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$PWD/tools/research/store.pod.toml
mkdir -p /workspace/c1
for spec in "$@"; do
  row=${spec%%=*}; art=${spec#*=}; d=/workspace/c1/records-$row
  rm -rf "$d"
  if python -m research.cli data fetch "$art" --to "$d" > /workspace/c1/fetch-$row.log 2>&1; then echo "ok $row $(du -sh "$d" | cut -f1)"; else echo "FAIL $row"; tail -5 /workspace/c1/fetch-$row.log; fi
done
rm -f /root/r2ro.env; unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
test -e /root/r2ro.env && echo "KEY-STILL-PRESENT" || echo "key deleted"
