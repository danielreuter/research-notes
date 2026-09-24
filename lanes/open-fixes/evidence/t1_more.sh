#!/bin/bash
# t1_more.sh FIRST LAST REL ... -- extra interleaved bench-vu A/B rounds (--zk, same flags as t1_chain.sh), order alternating
# base/lane on odd rounds and lane/base on even ones so slow drift of the pod cancels; results bench_<rel>_<tree>_r<N>.json
PY=/workspace/venv312/bin/python
export PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
L=/workspace/logs; O=/workspace/t1
log() { echo "$(date -u +%H:%M:%S) $*" >> $L/t1.log; }
B="bench-vu --mode interactive --batch 16384 --pipeline 4 --total-vus 4096 --reps 3 --device cuda --instances-cache /workspace/instances-cache --zk"
first=$1; last=$2; shift 2
for round in $(seq $first $last); do
  order="base lane"; [ $((round % 2)) = 0 ] && order="lane base"
  for rel in "$@"; do
    for t in $order; do
      tree=/workspace/src; [ $t = base ] && tree=/workspace/src-base
      tag=t1_bench_${rel}_${t}_r$round
      /workspace/run.sh $tree $tag $PY -m backends.direct.ligero.run --relation $rel $B --out $O/bench_${rel}_${t}_r$round.json
      log "bench $rel $t round $round --zk: $(tail -1 $L/$tag.log)"
    done
  done
done
log "T1_MORE_DONE $first..$last"
