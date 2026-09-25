#!/usr/bin/env bash
# x4-sha256-fill: one detached job per pod.  Bootstrap (host-memory check), optionally the fixture + gate (GATE=1, 10-gate.sh;
# the sweep runs only if it passes), the plateau sweep (40-sweep.sh: sweep_vu, --commit-per-rep, 5 reps, pinned Rust check on
# the plateau dump), then the instance-equiv/v1 document at the plateau size and its producer-side --check.
#   research run --on POD --project verity --cwd /workspace/src --custody-r2 --custody-ttl 8h \
#     --send lib.sh --send 00-bootstrap.sh --send 10-gate.sh --send 20-cell.sh --send 40-sweep.sh --send 50-outputs.py \
#     --env BASE=fp8-ada-x4 --env L=4096 --env PP=2 --env MAX=32768 -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/20-cell.sh"'
set -uo pipefail
IN=$(dirname "$0"); RD=${RESEARCH_RUN_DIR:?}; BASE=${BASE:?}
echo "##### $(date -u +%H:%M:%SZ) bootstrap RELS=$BASE BENCH_INSTANCES=${BENCH_INSTANCES:-0}"
RELS=$BASE bash "$IN/00-bootstrap.sh"
grep -q "^export" /workspace/env.sh 2>/dev/null || { echo "BOOTSTRAP: no env.sh"; exit 2; }
if [ "${GATE:-0}" = 1 ]; then
  echo "##### $(date -u +%H:%M:%SZ) gate"
  bash "$IN/10-gate.sh" || { echo "GATE FAILED: no sweep"; exit 4; }
fi
[ "${SWEEP:-1}" = 1 ] || exit 0
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
