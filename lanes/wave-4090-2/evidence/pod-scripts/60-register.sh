#!/usr/bin/env bash
# wave-4090-2 (laptop side): register pod runs in the evidence store, one at a time, then drop the transient copy.
#   dumped (local) run TAG: run-files/v1 tree (result.json, log, proofs/ incl. rust_batch.json) + bench-result/v1 (meta =
#     result.json + label/lane/tag, ref run_files=<tree>), both --preserve (reverify.py can fetch it later);
#   live run TAG: bench-result/v1 (meta = result.json + label/lane/tag), ref pair=<the local cell's bench-result> if PAIR=art:...
# Prints "TAG tree=art:... result=art:..." lines on stdout; appends them to $OUT.
# Usage: SSH="ssh ... root@IP" OUT=file bash 60-register.sh TAG[=LABEL] ...
set -uo pipefail
R=~/.research/bin/research
TMP=${TMPDIR:-/tmp}/wave-4090-2-reg; mkdir -p $TMP
for arg in "$@"; do
  tag=${arg%%=*}; label=${arg#*=}; [ "$label" = "$arg" ] && label=$tag
  d=$TMP/$tag; rm -rf $d; mkdir -p $d
  rsync -a -e "${SSH% root@*}" "root@${SSH##* root@}:/workspace/wave-4090/runs/$tag/" $d/ || { echo "$tag rsync failed"; continue; }
  python3 - "$d/result.json" "$label" "$tag" > $d.meta.json <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
r.update(label=f"wave-4090-2 {sys.argv[2]}", lane="wave-4090-2", tag=sys.argv[3], pod="vy-wave-4090 (RTX 4090, EU-RO-1)")
print(json.dumps(r))
PY
  refs=()
  tree=""
  if [ -d $d/proofs ]; then
    tree=$($R data put --kind run-files/v1 --tree $d --meta "{\"lane\": \"wave-4090-2\", \"tag\": \"$tag\", \"label\": \"wave-4090-2 $label\"}" --preserve | grep -o 'art:[0-9a-f]*' | tail -1)
    [ -n "$tree" ] || { echo "$tag tree put failed"; continue; }
    refs=(--ref run_files=$tree)
  fi
  [ -n "${PAIR:-}" ] && refs+=(--ref pair=$PAIR)
  res=$($R data put --kind bench-result/v1 --meta @$d.meta.json ${refs[@]+"${refs[@]}"} --preserve | grep -o 'art:[0-9a-f]*' | tail -1)
  echo "$tag tree=${tree:-none} result=${res:-FAILED}" | tee -a ${OUT:-/dev/null}
  rm -rf $d $d.meta.json
done
