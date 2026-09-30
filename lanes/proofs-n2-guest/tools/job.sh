#!/usr/bin/env bash
# proofs-n2-guest: one Verity guest fill job on vy-nebius-2 (run by the fill runner, whose cwd /workspace/pouw/fill it never writes).
#   job.sh stage IDX                    gpus=0: stage shape IDX (its line in shapes.tsv) of the Llama-3.2-1B row into the stage cache
#                                       (73-sweep-shape.sh MODE=stage), with a stub nvidia-smi so a CPU job makes no NVML calls
#   job.sh chunk IDX START COUNT GATE   gpus=1: prove COUNT statements of that shape's whole row (MODE=shape RUNS=COUNT WARM=1), as
#                                       backend-sweep-2's (b) chunks do; GATE=1 adds the GPU selftest (the device's paths against each
#                                       other and against the CPU prover, proofs and transcripts byte for byte)
# Idempotent: a job whose done/<id>.json exists (written only by verify.py, once its checks pass) exits 0 at once. Rerunnable from the
# top: every attempt starts in a fresh run dir, so a stop (window, waiter, max_min) loses only that attempt.
# PN2G_QUESTION is the job's research question (Daniel's rule, 2:53 PM PDT): a script without one is withdrawn and exits 0 at once.
set -uo pipefail
G=/workspace/verity-guest/wholerow
ROW=llama32-1b__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__greedy__bi-eager
BIN_SHA=e484a3352c4c3786ebe2bb06dde1343058ce5b6ca3c70f3e6c03d70207078af7   # flock-circuit of bin-4d568a3cb558b005-g1-sm120 (#554's draft key)
kind=${1:?stage or chunk} idx=${2:?shape index}
[ -e $G/STOP ] && { echo "$G/STOP exists: nothing to do"; exit 0; }
[ -n "${PN2G_QUESTION:-}" ] || { echo "no research question (PN2G_QUESTION): withdrawn, nothing to do"; exit 0; }
SHAPE=$(sed -n "$((idx + 1))p" $G/sweep2/$ROW/shapes.tsv | cut -f1)
[ ${#SHAPE} = 64 ] || { echo "no shape at line $idx of shapes.tsv"; exit 2; }
start= count= gate=
case $kind in
  stage) ID=pn2g-$idx-stage ;;
  chunk) start=${3:?} count=${4:?} gate=${5:?}; ID=pn2g-$idx-r$start ;;
  *) echo "kind $kind?"; exit 2 ;;
esac
OK=$G/done/$ID.json
[ -s $OK ] && { echo "$ID is done ($OK)"; exit 0; }
# the runner requeues a job it stopped at max_min without counting a try, so a job that can't fit in max_min would rerun forever
if [ -n "${FILL_JOB:-}" ] && grep -F "\"job\": \"$FILL_JOB\"" /workspace/pouw/fill/events.jsonl 2>/dev/null | grep -q '"why": "max_min"'; then
  echo "$(date -u +%FT%TZ) $ID refused: $FILL_JOB was stopped at max_min before" | tee -a $G/runs/$ID.attempts; exit 3
fi
R=$G/runs/$ID; rm -rf $R; mkdir -p $R
echo "$(date -u +%FT%TZ) $ID start job=${FILL_JOB:-} CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-} GPU_LEASE_UUID=${GPU_LEASE_UUID:-}" >> $G/runs/$ID.attempts
export SWEEP=$G/sweep2 FLOCK_WORK=$G/flock FLOCK_STAGE_CACHE=$G/flock/stage-cache SM=120 PYBIN=$G/flock/flock-circuit/py/bin/python3 \
  RESEARCH_RUN_DIR=$R
cd $G/tree || exit 2
t0=$(date +%s)
if [ $kind = stage ]; then
  export PATH=$G/stub:$PATH
  bash backends/flock/pod/73-sweep-shape.sh MODE=stage ROW=$ROW SHAPES=$SHAPE > $R/job.log 2>&1; rc=$?
else
  PORT=$($PYBIN -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
  ST=(); [ "$gate" = 1 ] && ST=(SELFTEST_SHAPES=$SHAPE SELFTEST_GPU=1)
  bash backends/flock/pod/73-sweep-shape.sh MODE=shape ROW=$ROW SHAPES=$SHAPE RUNS=$count WARM=1 FLOCK_KEEP_SESSIONS=3 PORT=$PORT \
    SUMMARY=$R/summary.json "${ST[@]}" > $R/job.log 2>&1; rc=$?
fi
$PYBIN $G/bin/verify.py "$kind" "$R" "$OK" "$rc" "$t0" "$(date +%s)" "$SHAPE" "$idx" "$start" "$count" "$gate" "$BIN_SHA"; v=$?
# the staged statement lives on in the stage cache; the run dir keeps only records and logs
[ $v = 0 ] && find $R/out -type f \( -name '*.bin' -o -name circuit.txt \) -delete
exit $v
