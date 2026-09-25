#!/bin/bash
# Coordinator sweep (read-only, 14:16Z): every 20 min log open/STALE lanes and research spend. It never renders, routes or reaps
# (the steward on vy-control-verity does those). Run from a stable directory: cd ~ && nohup bash .../sweep.sh &
E=~/.research/notes/lanes/coordinator/evidence
while true; do
  {
    echo "== $(date -u +%FT%TZ)"
    ~/.research/bin/research notes status 2>&1 | awk 'NR==1 || / open / || /STALE/'
    (cd $E && ~/projects/verity-main-wt/main/.venv/bin/python spend-ledger.py --report 2>&1 | head -1)
  } >> $E/sweep.log
  sleep 1200
done
