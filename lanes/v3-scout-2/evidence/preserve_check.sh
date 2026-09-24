#!/bin/bash
# preserve_check.sh LIST OUT : `research data preserved --mode head` for every art id in LIST not yet PRESERVED in OUT, 3 at a time,
# up to 6 passes (parallel runs can hit "database is locked" on the laptop catalog; a re-run then succeeds). Appends to OUT.
set -a; source ~/.config/verity/r2.env; set +a
export PYTHONPATH=~/projects/verity-main-wt/qol/tools/research/src
cd ~/projects/verity-main-wt/v3-scout-2
LIST=$1; OUT=$2; touch $OUT
for pass in 1 2 3 4 5 6; do
  TODO=$(while read a; do grep -q "^$a .*PRESERVED" $OUT || echo $a; done < $LIST)
  [ -z "$TODO" ] && { echo "ALL_PRESERVED pass=$pass $(date -u +%H:%M:%S)" >> $OUT; exit 0; }
  echo "$TODO" | xargs -P 3 -I{} sh -c 'sleep $((RANDOM % 5)); ~/projects/verity-main-wt/main/.venv/bin/python -m research data preserved {} --mode head 2>&1 | head -1' >> $OUT
done
echo "PASSES_EXHAUSTED $(date -u +%H:%M:%S)" >> $OUT
