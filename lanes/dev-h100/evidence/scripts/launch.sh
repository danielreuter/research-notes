#!/bin/bash
# launch.sh STAGE [extra research-run flags...] -- CMD...  : research run on vy-dev-h100 from the dev-h100 worktree (frozen 64c00bd),
# polls to completion, prints RUN=<id>.  @RD@ in CMD is replaced by the run dir, @ID@ by the run id.
set -u
cd /Users/danielreuter/projects/verity-main-wt/dev-h100
SSH=/tmp/devh100/ssh.sh
LOG=/tmp/devh100/drive.log
stage=$1; shift
EXTRA=()
while [ "$1" != "--" ]; do EXTRA+=("$1"); shift; done; shift
ID=$(uv run -q python -c "from research.runs import new_run_id; print(new_run_id())" 2>/dev/null | tail -1)
RD=/workspace/research/runs/$ID
CMD=()
for a in "$@"; do b="${a//@RD@/$RD}"; CMD+=("${b//@ID@/$ID}"); done
echo "=== $(date -u +%H:%M:%S) $stage -> $ID : ${CMD[*]}" >> $LOG
out=$(uv run -q research run --on vy-dev-h100 --project verity --campaign r23-dev-h100 --source /Users/danielreuter/projects/verity-main-wt/dev-h100 --exclusive --id "$ID" --stage "$stage" \
      --env PYTHONPATH=packages/verity/src:backends/numerical/python:tools/research/src:. --env PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
      "${EXTRA[@]}" -- "${CMD[@]}" 2>&1 | grep -v -E '^(Uninstalled|Installed)')
echo "$out" >> $LOG
if ! echo "$out" | grep -q "launched on vy-dev-h100"; then echo "LAUNCH FAILED: $out"; exit 3; fi
echo "$stage $ID" >> /tmp/devh100/runs.txt
t0=$(date +%s)
sleep 15
while true; do
  st=$($SSH "python3 -c \"import json;s=json.load(open('$RD/status.json'));print(s['transitions'][-1]['state'], s.get('rc'))\" 2>/dev/null" 2>/dev/null)
  case "${st%% *}" in done|failed|cancelled) break;; esac
  sleep 10
done
W=$(( $(date +%s) - t0 ))
echo "$(date -u +%H:%M:%S) $stage $ID state=$st wall=${W}s" | tee -a $LOG
echo "RUN=$ID"
