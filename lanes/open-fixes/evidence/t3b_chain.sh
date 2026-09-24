#!/bin/bash
# t3b_chain.sh -- lane open-fixes task 3 follow-ups on the 4090 (fixed tree /workspace/src):
#   gate-vu fp8-ada-v3 (--zk and plain; the negatives used to crash in privsel/hints.py on graph replay), then the folded
#   fp8-ada-v3x4 pipelined (l = 16384 at depth 2 -- depth 4 OOMs the 24 GB part for x4 -- and l = 4096 at depth 4), dumps Rust-verified
PY=/workspace/venv312/bin/python
L=/workspace/logs; O=/workspace/t3b; mkdir -p $O
log() { echo "$(date -u +%H:%M:%S) $*" >> $L/t3b.log; }
for z in --zk ""; do
  tag=t3b_gate${z:+zk}_v3
  /workspace/run.sh /workspace/src $tag $PY -m backends.direct.ligero.run --relation fp8-ada-v3 gate-vu --vus 2048 --batch 16384 --device cuda --instances-cache /workspace/instances-cache $z
  log "gate fp8-ada-v3 ${z:-plain}: $(tail -1 $L/$tag.log)"
done
for spec in 16384:2 4096:4; do
  IFS=: read batch depth <<< "$spec"
  tag=t3b_v3x4_l${batch}_p${depth}
  /workspace/run.sh /workspace/src $tag $PY -m backends.direct.ligero.run --relation fp8-ada-v3x4 bench-vu --zk --mode interactive --batch $batch --pipeline $depth --total-vus 4096 --reps 3 --device cuda --instances-cache /workspace/instances-cache --dump-dir $O/dump_$tag --dump-reps 1 --out $O/$tag.json
  log "bench $tag: $(tail -1 $L/$tag.log)"
  /workspace/bin/ligero-verify batch --system $O/dump_$tag/system.bin --dir $O/dump_$tag/rep1 > $L/${tag}_rust.log 2>&1
  log "rust $tag rc=$? $(tail -1 $L/${tag}_rust.log | cut -c1-200)"
done
log T3B_DONE
