#!/usr/bin/env bash
# fused-phases (laptop): EVERY Table 2 reject reason (the md render prints only the first) for the given art prefixes, from
# the frozen renderer at the lane tip and from tables-fix's (reads instance-equiv/v1).  Usage: bash 70-reasons.sh 06be3b23 ...
PY=~/projects/verity-main-wt/main/.venv/bin/python
for wt in fused-phases tables-fix; do
  (cd ~/projects/verity-main-wt/$wt/backends/numerical/python &&
   $PY -m verity_numerical.bench.tables --root ~/.research/store --format json > /tmp/fp_tables_$wt.json 2>/dev/null)
  echo "== $wt renderer"
  $PY - /tmp/fp_tables_$wt.json "$@" <<'EOF'
import json, sys
d, want = json.load(open(sys.argv[1])), sys.argv[2:]
for r in d["rejected"]:
    s = json.dumps(r)
    for w in want:
        if w in s:
            print(f"  {w}: " + " | ".join(r["reasons"]))
cells = json.dumps(d["table2"])
for w in want:
    if w in cells:
        print(f"  {w}: IN TABLE 2")
EOF
done
