#!/usr/bin/env bash
# x4-sha256-fill: one detached job per pod.  Bootstrap (host-memory check), optionally the fixture + gate (GATE=1, 10-gate.sh;
# the sweep runs only if it passes), the plateau sweep (40-sweep.sh: sweep_vu, --commit-per-rep, 5 reps, pinned Rust check on
# the plateau dump), then the instance-equiv/v1 document at the plateau size and its producer-side --check.
#   research run --on POD --project verity --cwd /workspace/src --custody-r2 --custody-ttl 8h \
#     --send lib.sh --send 00-bootstrap.sh --send 10-gate.sh --send 20-cell.sh --send 40-sweep.sh --send 50-outputs.py \
#     --env BASE=fp8-ada-x4 --env SCREEN="2048:2 2048:3 1024:4" --env MAX=32768 -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/20-cell.sh"'
set -uo pipefail
IN=$(dirname "$0"); RD=${RESEARCH_RUN_DIR:?}; BASE=${BASE:?}
echo "##### $(date -u +%H:%M:%SZ) bootstrap RELS=$BASE BENCH_INSTANCES=${BENCH_INSTANCES:-0}"
[ "${SKIP_BOOT:-0}" = 1 ] || RELS=$BASE bash "$IN/00-bootstrap.sh"
grep -q "^export" /workspace/env.sh 2>/dev/null || { echo "BOOTSTRAP: no env.sh"; exit 2; }
if [ "${GATE:-0}" = 1 ]; then
  echo "##### $(date -u +%H:%M:%SZ) gate"
  bash "$IN/10-gate.sh" || { echo "GATE FAILED: no sweep"; exit 4; }
fi
[ "${SWEEP:-1}" = 1 ] || exit 0
source /workspace/env.sh
if [ -n "${SCREEN:-}" ]; then  # SCREEN="l:p ...": per-proof settings screen at SCREEN_VUS, 2 reps, no dump; the fastest one sweeps
  best=0
  for c in $SCREEN; do
    IFS=: read -r l p <<<"$c"; o=$RD/screen/l$l-p$p; mkdir -p $o
    echo "##### $(date -u +%H:%M:%SZ) screen l$l p$p ${SCREEN_VUS:-4096} VUs"
    $PY -u -m backends.direct.ligero.run --relation $BASE+sha256 bench-vu --zk --mode interactive --auth included-hash --commit-per-rep \
        --batch $l --pipeline $p --total-vus ${SCREEN_VUS:-4096} --target -128 --reps 2 --device cuda --instance-procs 16 \
        --out $o/result.json > $o/bench.log 2>&1
    r=$?; v=$($PY -c "import json;m={x['name']:x['value'] for x in json.load(open('$o/result.json'))['measurements']};print(m['e2e.vu_per_second'], m.get('mem.peak_device_bytes'))" 2>/dev/null)
    echo "rc=$r vu/s,peak=$v $(grep -m1 -o 'OutOfMemoryError' $o/bench.log)"
    v=${v%% *}
    [ $r -eq 0 ] && [ -n "$v" ] && $PY -c "import sys;sys.exit(0 if float('$v')>float('$best') else 1)" && { best=$v; L=$l; PP=$p; }
  done
  [ "$best" = 0 ] && { echo "SCREEN: nothing ran"; exit 7; }
  echo "SCREEN: chose l$L p$PP ($best VU/s)"
fi
echo "##### $(date -u +%H:%M:%SZ) sweep $BASE+sha256 l${L:?} p${PP:?}"
SWEEPS="$BASE+sha256:$L:$PP" bash "$IN/40-sweep.sh"; src=$?
SD=$RD/$(echo "$BASE+sha256-l$L-p$PP" | tr '+' '_')
source /workspace/env.sh
N=$($PY -c "import json;d=json.load(open('$SD/sweep.json'));print([p['total_vus'] for p in d['points'] if p['point']==d['plateau_point']][0])") || { echo "no plateau"; exit 6; }
echo "##### $(date -u +%H:%M:%SZ) instance-equiv $BASE at the plateau, $N VUs"
mkdir -p $RD/outputs; F=$RD/outputs/instance-equiv-$BASE-$N.json
NT=${VY_CPU_THREADS:-8}
$PY -m verity_numerical.bench.instance_equiv --relation $BASE --vus $N --procs $NT --out $F; echo "equiv rc=$?"
$PY -m verity_numerical.bench.instance_equiv --check $F --vus $N --procs $NT; echo "equiv check rc=$?"
exit $src
