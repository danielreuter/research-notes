#!/usr/bin/env bash
# b-ligero-standard-hash: the x4 fold on the existing gadget (fp8-ada-x4+blake3, pinned 1168788f...: 12 columns per VU, two
# whole compressions per role per column, no half-block discard) -- a short probe per (l, pipeline) at 4096 VUs, 2 timed
# reps, --commit-per-rep, to pick the sweep's settings on the 4090 (24 GB).  Not a Table 2 point.
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 60-fold.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/60-fold.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}; REL=${REL:-fp8-ada-x4+blake3}
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
for cfg in ${CFGS:-4096:2 2048:2 2048:3}; do
  L=${cfg%%:*}; P=${cfg##*:}; tag=l${L}p${P}
  gpu_idle || exit 3
  $PY -m backends.direct.ligero.run --relation $REL bench-vu --zk --mode interactive --auth included-hash --commit-per-rep \
      --batch $L --pipeline $P --total-vus ${N:-4096} --target -128 --reps 2 --device cuda --out $RD/$tag.json > $RD/$tag.log 2>&1
  echo "$tag rc=$?"; grep -E "^rep |^config|committed|Error|error" $RD/$tag.log | cut -c1-330 | tail -n 5
  $PY -c "
import json,sys
r=json.load(open('$RD/$tag.json'))
m={x['name']: x['value'] for x in r.get('measurements', [])}
print('$tag', {k: m.get(k) for k in ('e2e.seconds','e2e.vu_per_second','commit.seconds','t.total') + tuple(k for k in m if k.startswith(('mem.', 'soundness.', 'census.')))})
" 2>&1 | tail -n 2
done
