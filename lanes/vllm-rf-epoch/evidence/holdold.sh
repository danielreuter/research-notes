#!/bin/bash
# holdold.sh FIXSHA: stop any row Commit whose tree (process cwd) is not the fixed tree FIXSHA (the pre-fix recording trees hit M >= 2^32);
# Commits from FIXSHA run. Ends when no rows.sh/after.sh/commitonly.sh is left, or after 8 h.
FIX=$1
for i in $(seq 1 5760); do
  for pid in $(pgrep -f "ops/(row_pod|tp_stage)\.sh .* commit$"); do
    cwd=$(readlink /proc/$pid/cwd 2>/dev/null)
    case "$cwd" in *"$FIX"*) ;; *)
      echo "$(date -u +%FT%TZ) holding pre-fix Commit (cwd $cwd): $(ps -o args= -p $pid | cut -c1-160)" >> $RESEARCH_RUN_DIR/hold.txt
      kill -TERM $pid ;;
    esac
  done
  pgrep -f "^bash .*inputs/(rows|after|commitonly)\.sh" > /dev/null || { echo "$(date -u +%FT%TZ) nothing left" >> $RESEARCH_RUN_DIR/hold.txt; exit 0; }
  sleep 5
done
