#!/bin/bash
# bench.sh STAGE RELATION BATCH PIPELINE [extra bench-vu flags e.g. --auth included-hash] -- one Table 2 column row on vy-dev-h100 from the
# frozen tree: interactive ZK, LIVE verifier, --target -128 --total-vus 4096 --reps 3, dumps of rep1, --instance-procs 16.  Polls; prints RUN=<id>.
set -u
cd /Users/danielreuter/projects/verity-main-wt/dev-h100
SSH=/tmp/devh100/ssh.sh
LOG=/tmp/devh100/drive.log
stage=$1; rel=$2; batch=$3; pipe=$4; shift 4
PYP=PYTHONPATH=packages/verity/src:backends/numerical/python:tools/research/src:.
ID=$(uv run -q python -c "from research.runs import new_run_id; print(new_run_id())" 2>/dev/null | tail -1)
RD=/workspace/research/runs/$ID
echo "=== $(date -u +%H:%M:%S) $stage ($rel batch=$batch pipeline=$pipe $*) -> $ID" >> $LOG
out=$(uv run -q research run --on vy-dev-h100 --project verity --campaign r23-dev-h100 --source /Users/danielreuter/projects/verity-main-wt/dev-h100 --exclusive --id "$ID" \
      --tool bench_vu_fp8 --scratch triton --require-result --stage "$stage" --env $PYP --env PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin -- \
      /workspace/venv312/bin/python -m backends.direct.ligero.run --relation "$rel" bench-vu --zk --mode interactive --verifier tcp://213.173.105.69:30899 \
      --target -128 --total-vus 4096 --reps 3 --batch "$batch" --pipeline "$pipe" --device cuda --instance-procs 16 --instances-cache /workspace/instances-cache \
      --run-id "$ID" --out "$RD/result.json" --dump-dir "$RD/proofs" --dump-reps 1 "$@" 2>&1 | grep -v -E '^(Uninstalled|Installed)')
echo "$out" >> $LOG
if ! echo "$out" | grep -q "launched on vy-dev-h100"; then echo "LAUNCH OUTPUT: $out"; exit 3; fi
echo "$stage $rel $ID" >> /tmp/devh100/runs.txt
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
