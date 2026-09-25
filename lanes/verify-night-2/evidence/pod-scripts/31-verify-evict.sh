#!/usr/bin/env bash
# verify-night-2: mark every artifact my scripts fetched as verified-preserved in the runner's store, then evict to free disk.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
export RESEARCH_STORE=/workspace/research/store
n=0; ok=0
while read -r A; do n=$((n+1)); $PY -m research data verify $A >/dev/null 2>&1 && ok=$((ok+1)); done < $RESEARCH_RUN_DIR/inputs/vn2-arts.txt
echo "verified $ok / $n"
$PY -m research data evict --target-free-gb 30 2>&1 | tail -2
df -h / | tail -1
