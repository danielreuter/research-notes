#!/usr/bin/env bash
# arith (laptop side): register pod runs in the evidence store, one at a time, then drop the transient copy.
#   TAG[=LABEL]      run-files/v1 tree (result.json, log, proofs/) + bench-result/v1 (meta = result.json + label/lane/tag,
#                    ref run_files=<tree>), both --preserve;
#   meta:TAG[=LABEL] bench-result/v1 only (result.json + log; no proofs pulled).
# Appends "TAG tree=art:... result=art:..." to evidence/registered.txt.
# Usage: POD="vy-arith (RTX 4090, EU-RO-1)" SSH="ssh -i KEY -p PORT root@IP" bash register.sh TAG ...
set -uo pipefail
R=~/.research/bin/research
OUT=~/.research/notes/lanes/arith/evidence/registered.txt
TMP=${TMPDIR:-/tmp}/arith-reg; mkdir -p $TMP
for arg in "$@"; do
  mode=tree; [ "${arg#meta:}" != "$arg" ] && { mode=meta; arg=${arg#meta:}; }
  tag=${arg%%=*}; label=${arg#*=}; [ "$label" = "$arg" ] && label=$tag
  d=$TMP/$tag; rm -rf $d; mkdir -p $d
  src="root@${SSH##* root@}:/workspace/arith/runs/$tag/"
  if [ $mode = tree ]; then
    rsync -a -e "${SSH% root@*}" "$src" $d/ || { echo "$tag rsync failed"; continue; }
  else
    rsync -a -e "${SSH% root@*}" --exclude proofs "$src" $d/ || { echo "$tag rsync failed"; continue; }
  fi
  python3 - "$d/result.json" "$label" "$tag" "$POD" > $d.meta.json <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
r.update(label=f"arith {sys.argv[2]}", lane="arith", tag=sys.argv[3], pod=sys.argv[4])
print(json.dumps(r))
PY
  refs=()
  tree=""
  if [ $mode = tree ]; then
    tree=$($R data put --kind run-files/v1 --tree $d --meta "{\"lane\": \"arith\", \"tag\": \"$tag\", \"label\": \"arith $label\"}" --preserve | grep -o 'art:[0-9a-f]*' | tail -1)
    [ -n "$tree" ] || { echo "$tag tree put failed"; continue; }
    refs=(--ref run_files=$tree)
  fi
  res=$($R data put --kind bench-result/v1 --meta @$d.meta.json ${refs[@]+"${refs[@]}"} --preserve | grep -o 'art:[0-9a-f]*' | tail -1)
  echo "$tag tree=${tree:-none} result=${res:-FAILED}" | tee -a $OUT
  rm -rf $d $d.meta.json
done
