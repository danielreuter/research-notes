#!/bin/bash
# t1_bx.sh REL:VUS_PER_SUB:SUBS ... -- task 1 stage 1 alone (seeded byte-identity base vs lane, --zk, interactive, --pipeline 4,
# + Rust batch verify of the lane files); for the H100, where the chain's first attempt hit bitexact.py's old coins_factory.
PY=/workspace/venv312/bin/python
export PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
L=/workspace/logs; O=/workspace/t1; mkdir -p $O $L
log() { echo "$(date -u +%H:%M:%S) $*" >> $L/t1.log; }
for spec in "$@"; do
  IFS=: read rel vus subs <<< "$spec"
  for t in base lane; do
    tree=/workspace/src; [ $t = base ] && tree=/workspace/src-base
    rm -rf $O/bx_${rel}_$t
    (cd $tree && PYTHONPATH=packages/verity/src:backends/numerical/python:. OMP_NUM_THREADS=4 \
      $PY /workspace/bitexact.py --tree $tree --rel $rel --zk --mode interactive --vus $vus --subs $subs --seed 7 --pipeline 4 \
      --out $O/bx_${rel}_$t > $L/t1_bx_${rel}_$t.log 2>&1)
    log "bx $rel $t rc=$?"
  done
  $PY /workspace/cmpdig.py $O/bx_${rel}_base $O/bx_${rel}_lane >> $L/t1.log 2>&1
  /workspace/bin/ligero-verify batch --system $O/bx_${rel}_lane/system.bin --dir $O/bx_${rel}_lane > $L/t1_bx_${rel}_rust.log 2>&1
  log "bx $rel lane rust rc=$? $(tail -1 $L/t1_bx_${rel}_rust.log | cut -c1-160)"
done
log T1_BX_DONE
