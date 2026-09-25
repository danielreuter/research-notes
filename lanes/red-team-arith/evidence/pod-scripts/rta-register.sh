#!/usr/bin/env bash
# red-team-arith (pod side, through research run --on): register this target's evidence, --preserve, then a bounded
# `research data preserved`.  Credential: /workspace/red-team-arith/.cred (minted on the laptop, ttl 4h).
#   bash rta-register.sh TARGET POD_LABEL CFG[:REV,REV...]...
#   - evidence tree: /workspace/red-team-arith/TARGET without the proof dumps (tests logs + json, per-run logs, result.json,
#     urandom traces, sha256 lists, ab-summary.txt)
#   - for each CFG: the listed revs' full run dirs (proofs included; default 22741456,tip)
# Appends "LABEL art:..." lines to /workspace/red-team-arith/registered.txt.
set -uo pipefail
source /workspace/env.sh
set -a; source /workspace/red-team-arith/.cred; set +a
R="$PY -m research"
T=$1 POD=$2; shift 2
B=/workspace/red-team-arith; A=$B/$T; OUT=$B/registered.txt
TIP=$(python3 -c 'import json; print(json.load(open("/workspace/src/.research-source.json"))["commit"])' 2>/dev/null)
put() {  # LABEL DIR
  local label=$1 dir=$2 art
  art=$($R data put --kind run-files/v1 --tree "$dir" --preserve \
        --meta "{\"lane\": \"red-team-arith\", \"label\": \"red-team-arith $label\", \"target\": \"$T\", \"pod\": \"$POD\", \"tree_commit\": \"$TIP\", \"subject\": \"lane/arith 92dab0ad vs main 22741456\"}" \
        2>/tmp/rta-put.err | grep -o 'art:[0-9a-f]*' | tail -1)
  echo "$label ${art:-FAILED $(tail -1 /tmp/rta-put.err)}" | tee -a $OUT
}
st=/tmp/rta-evidence-$T; rm -rf $st; mkdir -p $st
rsync -a --exclude proofs --exclude '*.pyc' $A/ $st/
put "$T evidence (tests + A/B summaries, no dumps)" $st
for spec in "$@"; do
  cfg=${spec%%:*}; revs=${spec#*:}; [ "$revs" = "$spec" ] && revs=22741456,tip
  for r in ${revs//,/ }; do
    [ -d $A/ab/$cfg/$r ] && put "$T $cfg $r run dir (proof dumps)" $A/ab/$cfg/$r
  done
done
arts=$(grep -o 'art:[0-9a-f]\{64\}' $OUT | sort -u)
for i in 1 2 3; do
  timeout 300 $PY -m research data preserved $arts > $B/preserved-$T.out 2>&1; rc=$?
  echo "preserved $T try $i rc=$rc: $(tail -1 $B/preserved-$T.out)" | tee -a $OUT
  [ $rc = 0 ] && break
done
cp $OUT ${RESEARCH_RUN_DIR:-/tmp}/ 2>/dev/null
echo DONE-register
