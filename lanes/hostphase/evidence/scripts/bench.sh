#!/bin/bash
# bench.sh STAGE SOURCE_DIR RELATION [bench-vu flags...]  -- one contract row (relchain.bench_vu_rel) on vy-hostphase, b-merge-h100's
# exact command line (--batch 16384 --total-vus 4096 --reps 3 --target -128, --dump-dir $RD/proofs --dump-reps 1); SOURCE_DIR = the
# git checkout shipped (main worktree for the baseline, the hostphase worktree for the lane).
set -u
cd /Users/danielreuter/projects/verity-main-wt/hostphase
SSH=/tmp/hostphase/ssh.sh
LOG=/tmp/hostphase/drive.log
stage=$1; src=$2; rel=$3; shift 3
PYP=PYTHONPATH=packages/verity/src:backends/numerical/python:.
ID=$(uv run python -c "from research.runs import new_run_id; print(new_run_id())" 2>/dev/null | tail -1)
RD=/workspace/research/runs/$ID
echo "=== $(date -u +%H:%M:%S) $stage ($src $rel $*) -> $ID" >> $LOG
out=$(uv run research run --on vy-hostphase --project verity --campaign r21-hostphase --source "$src" --exclusive --id "$ID" \
      --tool bench_vu_fp8 --scratch triton --require-result --stage "$stage" --env $PYP -- \
      /workspace/venv312/bin/python -m backends.direct.ligero.run --relation "$rel" bench-vu "$@" --batch 16384 --total-vus 4096 --reps 3 \
      --target -128 --device cuda --instance-procs 16 --instances-cache /workspace/instances-cache \
      --run-id "$ID" --out "$RD/result.json" --dump-dir "$RD/proofs" --dump-reps 1 2>&1 | grep -v -E '^(Uninstalled|Installed)')
echo "$out" >> $LOG
if ! echo "$out" | grep -q "launched on vy-hostphase"; then echo "LAUNCH OUTPUT: $out"; fi
echo "$stage $rel $ID" >> /tmp/hostphase/runs.txt
t0=$(date +%s)
sleep 20
while true; do
  st=$($SSH "python3 -c \"import json;s=json.load(open('$RD/status.json'));print(s['transitions'][-1]['state'], s.get('rc'))\" 2>/dev/null" 2>/dev/null)
  case "${st%% *}" in done|failed|cancelled) break;; esac
  sleep 10
done
W=$(( $(date +%s) - t0 ))
echo "$(date -u +%H:%M:%S) $stage $ID state=$st wall=${W}s" | tee -a $LOG
echo "RUN=$ID"
