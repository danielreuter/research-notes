#!/usr/bin/env bash
# b-ligero-standard-hash: main 94b1c4d2's GPU committer (commit-gpu, frame_gpu) under --commit-per-rep on the 4090 -- its unit
# tests, then fp8-ada+blake3 at N VUs (l = L, pipeline P, 2 timed reps) with the device committer and with host paths
# (LIGERO_COMMIT_GPU=0): the two runs' --commit-evidence (tree refs, level / digest / chain-state sha256) must be equal.
# Not a Table 2 point.
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 61-smoke.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/61-smoke.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}; REL=${REL:-fp8-ada+blake3}; N=${N:-4096}; L=${L:-4096}; P=${P:-2}
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
$PY -m pytest -q backends/direct/ligero/frame_gpu_test.py backends/shared/hash_gpu/tests/test_frame_v3.py 2>&1 | tail -n 6
echo "pytest rc=${PIPESTATUS[0]}"
for g in 1 0; do
  gpu_idle || exit 3
  LIGERO_COMMIT_GPU=$g $PY -m backends.direct.ligero.run --relation $REL bench-vu --zk --mode interactive --auth included-hash \
      --commit-per-rep --batch $L --pipeline $P --total-vus $N --target -128 --reps 2 --device cuda \
      --commit-evidence $RD/ev_gpu$g.json --out $RD/gpu$g.json > $RD/gpu$g.log 2>&1
  echo "gpu=$g rc=$?"; grep -E "^commit |^rep |committed|Error|error" $RD/gpu$g.log | cut -c1-330 | tail -n 6
  $PY -c "
import json
r = json.load(open('$RD/gpu$g.json'))
m = {x['name']: x['value'] for x in r.get('measurements', [])}
print('gpu=$g', {k: m.get(k) for k in ('commit.seconds', 'commit.cold_seconds', 't.total', 'e2e.seconds', 'e2e.vu_per_second')})
" 2>&1 | tail -n 2
done
$PY -c "
import json
a, b = (json.load(open('$RD/ev_gpu%d.json' % g)) for g in (1, 0))
print('commit evidence equal (device vs host):', a == b, a.get('sha256'), b.get('sha256'))
"
