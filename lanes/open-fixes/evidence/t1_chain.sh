#!/bin/bash
# t1_chain.sh REL:VUS_PER_SUB:SUBS ... -- lane open-fixes task 1 (hp2-host's CUDA NTT, e689b72) on one pod:
#   /workspace/src = lane HEAD (with the NTT), /workspace/src-base = the same tree with only e689b72 removed.
# In order of importance (the H100 is time-capped; later stages may be cut):
#   1. seeded byte-identity (hostphase bitexact.py: os.urandom -> SHAKE stream, so coins AND ZK mask keys repeat), --zk,
#      interactive, --pipeline 4, every sub-batch of 4096 VUs at l = 16384; digests compared; Rust batch verify of the lane dump
#   2. bench-vu A/B --zk, interleaved base/lane, two rounds; the lane's first round dumps rep 1
#   3. gate-vu --zk --vus 2048 --batch 16384 on the lane tree; Rust batch verify of the bench dumps; ntt_cuda_test
#   4. gate-vu (plain) on the lane tree; one bench-vu A/B round without --zk
PY=/workspace/venv312/bin/python
export PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
L=/workspace/logs; O=/workspace/t1; mkdir -p $O $L
log() { echo "$(date -u +%H:%M:%S) $*" >> $L/t1.log; }
tree_of() { [ "$1" = base ] && echo /workspace/src-base || echo /workspace/src; }
B="bench-vu --mode interactive --batch 16384 --pipeline 4 --total-vus 4096 --reps 3 --device cuda --instances-cache /workspace/instances-cache"
bench_round() {   # round zkflag specs...
  local round=$1 z=$2; shift 2
  for spec in "$@"; do
    IFS=: read rel vus subs <<< "$spec"
    for t in base lane; do
      extra=""; [ $t = lane ] && [ $round = 1 ] && extra="--dump-dir $O/dump_${rel}_lane --dump-reps 1"
      tag=t1_bench_${rel}_${t}_r$round
      /workspace/run.sh $(tree_of $t) $tag $PY -m backends.direct.ligero.run --relation $rel $B $z --out $O/bench_${rel}_${t}_r$round.json $extra
      log "bench $rel $t round $round ${z:-nozk}: $(tail -1 $L/$tag.log)"
    done
  done
}
gate() {   # zkflag specs...
  local z=$1; shift
  for spec in "$@"; do
    IFS=: read rel vus subs <<< "$spec"
    tag=t1_gate${z:+zk}_${rel}
    /workspace/run.sh /workspace/src $tag $PY -m backends.direct.ligero.run --relation $rel gate-vu --vus 2048 --batch 16384 \
      --device cuda --instances-cache /workspace/instances-cache $z
    log "gate $rel ${z:-plain}: $(tail -1 $L/$tag.log)"
  done
}
log "T1 start: $*  lane=$(cat /workspace/src/TREE_SHA) base=$(cat /workspace/src-base/TREE_SHA)"
for spec in "$@"; do
  IFS=: read rel vus subs <<< "$spec"
  for t in base lane; do
    tree=$(tree_of $t)
    (cd $tree && PYTHONPATH=packages/verity/src:backends/numerical/python:. OMP_NUM_THREADS=4 \
      $PY /workspace/bitexact.py --tree $tree --rel $rel --zk --mode interactive --vus $vus --subs $subs --seed 7 --pipeline 4 \
      --out $O/bx_${rel}_$t > $L/t1_bx_${rel}_$t.log 2>&1)
    log "bx $rel $t rc=$?"
  done
  $PY /workspace/cmpdig.py $O/bx_${rel}_base $O/bx_${rel}_lane >> $L/t1.log 2>&1
  /workspace/bin/ligero-verify batch --system $O/bx_${rel}_lane/system.bin --dir $O/bx_${rel}_lane > $L/t1_bx_${rel}_rust.log 2>&1
  log "bx $rel lane rust rc=$?"
done
bench_round 1 --zk "$@"
bench_round 2 --zk "$@"
gate --zk "$@"
for spec in "$@"; do
  IFS=: read rel vus subs <<< "$spec"
  for r in $O/dump_${rel}_lane/rep*; do
    /workspace/bin/ligero-verify batch --system $O/dump_${rel}_lane/system.bin --dir $r > $L/t1_dump_${rel}_rust_$(basename $r).log 2>&1
    log "dump $rel $(basename $r) rust rc=$?"
  done
done
/workspace/run.sh /workspace/src t1_ntt_cuda_test $PY -m pytest -q -p no:cacheprovider backends/direct/ligero/ntt_cuda_test.py
log "ntt_cuda_test: $(grep -E 'passed|failed' $L/t1_ntt_cuda_test.log | tail -1)"
log T1_CORE_DONE
gate "" "$@"
bench_round 3 "" "$@"
log T1_DONE
