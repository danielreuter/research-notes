#!/usr/bin/env bash
# fused-phases (laptop side): register pod runs, one at a time: run-files/v1 tree (result.json, log, proofs/) + bench-result/v1
# (meta = result.json + label / lane / tag, ref run_files=<tree>), both --preserve.  Keeps result.json + log under $KEEP for
# bench.summary / tables (proofs/ dropped once preserved).  Prints "TAG tree=art:... result=art:..." and appends it to $OUT.
# Usage: SSH="ssh ... root@IP" OUT=file KEEP=dir bash 60-register.sh TAG[=LABEL] ...
set -uo pipefail
R=~/.research/bin/research
set -a; source ~/.config/verity/r2.env; set +a
KEEP=${KEEP:-/tmp/fused-phases-runs}; mkdir -p $KEEP
for arg in "$@"; do
  tag=${arg%%=*}; label=${arg#*=}; [ "$label" = "$arg" ] && label=$tag
  d=$KEEP/$tag; rm -rf $d; mkdir -p $d
  rsync -a -e "${SSH% root@*}" "root@${SSH##* root@}:/workspace/fused-phases/runs/$tag/" $d/ || { echo "$tag rsync failed"; continue; }
  python3 - "$d/result.json" "$label" "$tag" > $d.meta.json <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
r.update(label=f"fused-phases {sys.argv[2]}", lane="fused-phases", tag=sys.argv[3], pod="vy-fused-phases (RTX 4090)")
print(json.dumps(r))
PY
  tree=$($R data put --kind run-files/v1 --tree $d --meta "{\"lane\": \"fused-phases\", \"tag\": \"$tag\", \"label\": \"fused-phases $label\"}" --preserve 2>&1 | grep -o 'art:[0-9a-f]*' | tail -1)
  [ -n "$tree" ] || { echo "$tag tree put failed"; continue; }
  res=$($R data put --kind bench-result/v1 --meta @$d.meta.json --ref run_files=$tree --preserve 2>&1 | grep -o 'art:[0-9a-f]*' | tail -1)
  echo "$tag tree=$tree result=${res:-FAILED}" | tee -a ${OUT:-/dev/null}
  rm -rf $d.meta.json $d/proofs   # the laptop keeps result.json + log only (contract §7: no dump trees)
done
