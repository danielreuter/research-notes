#!/bin/bash
# dev-h100-2 measurement driver (laptop). Usage: drive.sh STAGE REL AUTH(bare|hashed) BATCH PIPELINE REPS DUMP(0|1) LIVE(0|1) [MACHINE]
# Launches through `research run --on <machine>` and polls `research fetch` until the run leaves running/submitted.
set -uo pipefail
STAGE=$1; REL=$2; AUTH=$3; BATCH=$4; PIPE=$5; REPS=$6; DUMP=${7:-0}; LIVE=${8:-1}; MACH=${9:-vy-dev-h100-2b}
cd ~/projects/verity-main-wt/dev-h100-2 || exit 1
LOG=/tmp/dh2/logs/${STAGE}.log
IDS=/tmp/dh2/runs.txt
VER=${VERIFIER:-tcp://216.81.245.17:14776}
PYENV=PYTHONPATH=packages/verity/src:backends/numerical/python:tools/research/src:.
log() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG"; }
EXTRA=""; [ "$AUTH" = "hashed" ] && EXTRA="--auth included-hash"
DUMPARGS=""; [ "$DUMP" = "1" ] && DUMPARGS="--dump-dir \$RESEARCH_RUN_DIR/proofs --dump-reps 1"
LIVEARGS=""; [ "$LIVE" = "1" ] && LIVEARGS="--verifier $VER"
log "START $STAGE rel=$REL auth=$AUTH batch=$BATCH pipeline=$PIPE reps=$REPS dump=$DUMP live=$LIVE on=$MACH"
out=$(uv run -q research run --on $MACH --project verity --campaign r23-dev-h100-2 --source . --tool bench_vu_fp8 --scratch triton \
  --exclusive --require-result --stage "$STAGE" --env "$PYENV" --env OMP_NUM_THREADS=16 --env TORCH_NUM_THREADS=16 -- \
  /workspace/venv312/bin/python -m backends.direct.ligero.run --relation $REL bench-vu --zk --mode interactive \
  --batch "$BATCH" --pipeline "$PIPE" --total-vus 4096 --reps "$REPS" --target -128 --device cuda \
  $LIVEARGS --instance-procs 16 --instances-cache /workspace/instances-cache \
  $EXTRA $DUMPARGS --out '$RESEARCH_RUN_DIR/result.json' 2>&1 | grep -v -E '^(Uninstalled|Installed)')
echo "$out" >> "$LOG"
id=$(echo "$out" | grep -oE 'run r[0-9]{8}-[0-9]{6}-[0-9a-f]{4} launched' | head -1 | awk '{print $2}')
if [ -z "$id" ]; then log "launch FAILED for $STAGE: $out"; exit 1; fi
echo "$STAGE $id" >> "$IDS"; log "$STAGE -> $id"
while :; do
  sleep 10
  st=$(uv run -q research fetch "$id" 2>&1 | grep -oE 'observed \S+: [a-z]+' | awk '{print $3}')
  case "$st" in running|submitted|"") ;; *) break ;; esac
done
log "END $STAGE $id finished: $st"
uv run -q research fetch "$id" 2>&1 | tail -2 | tee -a "$LOG"
