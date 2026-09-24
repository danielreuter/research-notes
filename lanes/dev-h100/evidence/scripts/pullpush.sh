#!/bin/bash
# pullpush.sh RUN : brief §0/§3 store flow from the laptop: evict -> research data pull RUN --from vy-dev-h100 -> push --verify head -> evict.
# Prints the pulled artifact ids (result=art:..., run-files=art:...) and appends them to /tmp/devh100/store.log.
set -u
cd /Users/danielreuter/projects/verity-main-wt/dev-h100 || exit 2
set -a; source ~/.config/verity/r2.env; set +a
EV="python3 /tmp/store_evict.py --target-free-gb 6 --min-kb 16"
LOG=/tmp/devh100/store.log
run=$1
echo "=== $(date -u +%H:%M:%S) pull $run" | tee -a $LOG
$EV 2>&1 | tail -2 | tee -a $LOG
df -h / | tail -1 | tee -a $LOG
uv run -q research data pull "$run" --from vy-dev-h100 --project verity 2>&1 | tee /tmp/devh100/pull_$run.log | tail -25 | tee -a $LOG
echo "--- $(date -u +%H:%M:%S) push $run" | tee -a $LOG
uv run -q research data push "$run" --verify head 2>&1 | tee /tmp/devh100/push_$run.log | tail -15 | tee -a $LOG
$EV 2>&1 | tail -2 | tee -a $LOG
df -h / | tail -1 | tee -a $LOG
echo "=== $(date -u +%H:%M:%S) done $run" | tee -a $LOG
