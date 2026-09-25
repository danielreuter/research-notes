#!/usr/bin/env bash
set -uo pipefail
source /workspace/env.sh
cd /workspace/src-bls
O=/workspace/red-team-standard-hash/free-806a2f73; rm -rf $O; mkdir -p $O
cat .research-source.json > $O/source.json
start=$(date +%s)
$PY -m backends.direct.ligero.redteam.rtsh_blake3_free_rows --out $O > $O/free.log 2>&1; rc=$?
echo "rc=$rc wall=$(( $(date +%s) - start ))s"; cut -c1-400 $O/free.log | tail -20
