#!/usr/bin/env bash
# red-team-standard-hash: mutate-and-recompute scan of the sha256 leaf gadget at b-ligero-sha256 da74b03e (/workspace/src-sha2);
# waits for the final suite (rtsh-final-1050) to finish first.
set -uo pipefail
source /workspace/env.sh
while pgrep -f rtsh-main.sh > /dev/null; do sleep 20; done
cd /workspace/src-sha2
O=/workspace/red-team-standard-hash/free-sha-da74b03e; rm -rf $O; mkdir -p $O
cat .research-source.json > $O/source.json
start=$(date +%s)
$PY -m backends.direct.ligero.redteam.rtsh_blake3_free_rows --leaf sha256 --shapes 8:2,8:0.5 --control-shape 8:2 --out $O > $O/free.log 2>&1; rc=$?
echo "rc=$rc wall=$(( $(date +%s) - start ))s"; cut -c1-400 $O/free.log | tail -12
