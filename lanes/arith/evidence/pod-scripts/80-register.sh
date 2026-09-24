#!/usr/bin/env bash
# arith (pod side, via research run --on so the research package is on PYTHONPATH): register runs from /workspace/arith/runs.
#   bash 80-register.sh POD_LABEL SPEC...      SPEC = TAG=LABEL (run-files/v1 tree + bench-result/v1) | meta:TAG=LABEL (result only)
# Both --preserve.  Appends "TAG tree=art:... result=art:..." to /workspace/arith/registered.txt.
source /workspace/env.sh
set -a; source /workspace/arith/.cred; set +a
R="$PY -m research"
OUT=/workspace/arith/registered.txt
POD=$1; shift
for spec in "$@"; do
  mode=tree; [ "${spec#meta:}" != "$spec" ] && { mode=meta; spec=${spec#meta:}; }
  tag=${spec%%=*}; label=${spec#*=}; [ "$label" = "$spec" ] && label=$tag
  d=/workspace/arith/runs/$tag
  [ -f $d/result.json ] || { echo "$tag: no result.json" | tee -a $OUT; continue; }
  $PY - "$d/result.json" "$label" "$tag" "$POD" > /tmp/meta-$tag.json <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
r.update(label=f"arith {sys.argv[2]}", lane="arith", tag=sys.argv[3], pod=sys.argv[4])
print(json.dumps(r))
PY
  refs=(); tree=""
  if [ $mode = tree ]; then
    tree=$($R data put --kind run-files/v1 --tree $d --meta "{\"lane\": \"arith\", \"tag\": \"$tag\", \"label\": \"arith $label\"}" --preserve 2>/tmp/put-$tag.err | grep -o 'art:[0-9a-f]*' | tail -1)
    [ -n "$tree" ] || { echo "$tag tree put failed: $(tail -1 /tmp/put-$tag.err)" | tee -a $OUT; continue; }
    refs=(--ref run_files=$tree)
  fi
  res=$($R data put --kind bench-result/v1 --meta @/tmp/meta-$tag.json ${refs[@]+"${refs[@]}"} --preserve 2>/tmp/put-$tag.err | grep -o 'art:[0-9a-f]*' | tail -1)
  echo "$tag tree=${tree:-none} result=${res:-FAILED $(tail -1 /tmp/put-$tag.err)}" | tee -a $OUT
done
echo DONE-80
