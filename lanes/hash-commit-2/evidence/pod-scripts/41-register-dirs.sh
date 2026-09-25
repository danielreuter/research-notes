#!/usr/bin/env bash
# hash-commit-2 (pod): preserve small result dirs as run-files/v1 trees: bash 41-register-dirs.sh LABEL DIR...
# (commit_cost --impl gpu dirs, the Flock output, log copies). Same credential/store config as 40-register.sh (run that
# first, with no args, to write store.pod.toml). Appends to registered.txt.
set -uo pipefail
HC=/workspace/hash-commit-2
set -a; . $HC/r2.env; set +a
TOOL=$(ls -td /workspace/research/tool/*/ | head -1)
export PYTHONPATH=$TOOL RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$HC/store.pod.toml"
lab=$1; shift
for d in "$@"; do
  a=$(python3 -m research data put --kind run-files/v1 --tree $d --preserve \
    --meta "{\"lane\": \"hash-commit-2\", \"tag\": \"$(basename $d)\", \"label\": \"hash-commit-2 commit-gpu $lab $(basename $d)\", \"pod\": \"${POD_DESC:?POD_DESC}\"}" | grep -o 'art:[0-9a-f]*' | tail -1)
  echo "$(date -u +%H:%M:%SZ) $lab $d tree=${a:-FAILED}" | tee -a $HC/registered.txt
done
