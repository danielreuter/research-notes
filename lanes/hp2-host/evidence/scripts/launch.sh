#!/bin/bash
# launch.sh STAGE [extra research-run flags...] -- CMD...  : research run on vy-hp2-host from the hp2-host worktree (or --source DIR), polls to completion, prints RUN=<id>
set -u
cd /Users/danielreuter/projects/verity-main-wt/hp2-host
set -a; source ~/.config/verity/r2.env; set +a
SSH=/tmp/hp2/ssh.sh
LOG=/tmp/hp2/drive.log
POD=${POD:-vy-hp2-host}
stage=$1; shift
EXTRA=()
while [ "$1" != "--" ]; do EXTRA+=("$1"); shift; done; shift
ID=$(uv run python -c "from research.runs import new_run_id; print(new_run_id())" 2>/dev/null | tail -1)
RD=/workspace/research/runs/$ID
CMD=()
for a in "$@"; do CMD+=("${a//@RD@/$RD}"); done
echo "=== $(date -u +%H:%M:%S) $stage -> $ID : ${CMD[*]}" >> $LOG
out=$(uv run research run --on $POD --project verity --campaign r22-hp2-host --source . --exclusive --id "$ID" --stage "$stage" \
      --env PYTHONPATH=packages/verity/src:backends/numerical/python:tools/research/src:. --env PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
      "${EXTRA[@]}" -- "${CMD[@]}" 2>&1 | grep -v -E '^(Uninstalled|Installed)')
echo "$out" >> $LOG
if ! echo "$out" | grep -q "launched on $POD"; then echo "LAUNCH FAILED: $out"; exit 3; fi
echo "$stage $ID" >> /tmp/hp2/runs.txt
t0=$(date +%s)
while true; do
  st=$($SSH "python3 -c \"import json;s=json.load(open('$RD/status.json'));print(s['transitions'][-1]['state'], s.get('rc'))\" 2>/dev/null" 2>/dev/null)
  case "${st%% *}" in done|failed|cancelled) break;; esac
  sleep 10
done
W=$(( $(date +%s) - t0 ))
echo "$(date -u +%H:%M:%S) $stage $ID state=$st wall=${W}s" | tee -a $LOG
echo "RUN=$ID"
