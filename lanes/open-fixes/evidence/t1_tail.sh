#!/bin/bash
PY=/workspace/venv312/bin/python
export PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
L=/workspace/logs; O=/workspace/t1
log() { echo "$(date -u +%H:%M:%S) $*" >> $L/t1.log; }
B="bench-vu --mode interactive --batch 16384 --pipeline 4 --total-vus 4096 --reps 3 --device cuda --instances-cache /workspace/instances-cache"
for round in 8 9; do
  order="base lane"; [ $((round % 2)) = 0 ] && order="lane base"
  for rel in fp8-hopper bf16-hopper; do
    for t in $order; do
      tree=/workspace/src; [ $t = base ] && tree=/workspace/src-base
      tag=t1_bench_${rel}_${t}_r$round
      /workspace/run.sh $tree $tag $PY -m backends.direct.ligero.run --relation $rel $B --out $O/bench_${rel}_${t}_r$round.json
      log "bench $rel $t round $round nozk: $(tail -1 $L/$tag.log)"
    done
  done
done
for t in lane base; do
  tree=/workspace/src; [ $t = base ] && tree=/workspace/src-base
  for spec in fp8-hopper:341 bf16-hopper:170; do
    IFS=: read rel vus <<< "$spec"
    /workspace/run.sh $tree t1_dispatch_${rel}_$t $PY /workspace/ntt_dispatch.py $rel $vus
    log "dispatch $rel $t: $(grep NTT_DISPATCH $L/t1_dispatch_${rel}_$t.log)"
  done
done
log T1_TAIL_DONE
