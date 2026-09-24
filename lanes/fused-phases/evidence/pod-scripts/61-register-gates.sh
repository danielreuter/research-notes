#!/usr/bin/env bash
# fused-phases (laptop side): register gate-vu outputs as wave-4090-2 did: run-files/v1 tree {NAME.json, NAME.log} (evidence)
# + gate-report/v1 (payload NAME.json, ref evidence=<tree>, meta label / lane / relation), both --preserve.
# Usage: SSH="ssh ... root@IP" OUT=file bash 61-register-gates.sh NAME=RELATION=LABEL ...
set -uo pipefail
R=~/.research/bin/research
set -a; source ~/.config/verity/r2.env; set +a
TMP=${TMPDIR:-/tmp}/fused-phases-gates; mkdir -p $TMP
for arg in "$@"; do
  name=${arg%%=*}; rest=${arg#*=}; rel=${rest%%=*}; label=${rest#*=}
  d=$TMP/$name; rm -rf $d; mkdir -p $d
  for x in json log; do
    rsync -a -e "${SSH% root@*}" "root@${SSH##* root@}:/workspace/fused-phases/gates/$name.$x" $d/ || { echo "$name rsync failed"; continue 2; }
  done
  tree=$($R data put --kind run-files/v1 --tree $d --meta "{\"lane\": \"fused-phases\", \"tag\": \"gate-$name\", \"label\": \"fused-phases gate $name\"}" --preserve 2>&1 | grep -o 'art:[0-9a-f]*' | tail -1)
  [ -n "$tree" ] || { echo "$name tree put failed"; continue; }
  meta=$(python3 -c 'import json, sys; print(json.dumps({"label": "fused-phases " + sys.argv[1], "lane": "fused-phases", "relation": sys.argv[2]}))' "$label" "$rel")
  res=$($R data put --kind gate-report/v1 --file $d/$name.json --meta "$meta" --ref evidence=$tree --preserve 2>&1 | grep -o 'art:[0-9a-f]*' | tail -1)
  echo "gate-$name tree=$tree result=${res:-FAILED}" | tee -a ${OUT:-/dev/null}
done
