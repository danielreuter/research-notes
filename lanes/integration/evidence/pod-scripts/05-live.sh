#!/usr/bin/env bash
# integration merge-val-3 (e): live verifier on THIS pod (localhost, merged tree) + one live --zk interactive session each for
# fp8-ada bare and +shared (tile 64x64); Rust batch re-verifies every session dir
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
O=/workspace/integration/live; mkdir -p $O/sessions
setsid nohup $PY -m backends.direct.ligero.live serve --listen 127.0.0.1:7000 --out $O/sessions --jobs 4 --threads 1 \
  --target-bits 128 > $O/serve.out 2>&1 < /dev/null &
echo $! > $O/serve.pid
sleep 8
lv() {  # tag, relation, extra args...
  local tag=$1 rel=$2; shift 2
  rm -rf $O/$tag; mkdir -p $O/$tag
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch 16384 --pipeline 4 \
      --total-vus 4096 --target -128 --reps 1 --verifier tcp://127.0.0.1:7000 --out $O/$tag/result.json "$@" > $O/$tag/log 2>&1
  echo "$tag bench rc=$?" | tee -a $O/summary.txt
}
lv fp8-ada-bare fp8-ada
lv fp8-ada-shared fp8-ada --auth included-hash-shared --tile 64x64
sleep 5
cp $O/sessions/index.jsonl $O/index.jsonl 2>/dev/null
for d in $O/sessions/s*/; do
  [ -f $d/system.bin ] || continue
  hs=""; [ -f $d/system_h.bin ] && hs="--system-h $d/system_h.bin"
  $LIGERO_VERIFY batch --system $d/system.bin $hs --dir $d --target-bits 128 > $d/rust_batch.json 2> $d/rust_batch.err
  echo "$(basename $d) rust rc=$? $(grep -o '"accepted":[0-9]*,"rejected":[0-9]*' $d/rust_batch.json | head -1) $(grep -o '"system_pinned":[a-z]*' $d/rust_batch.json | head -1) $(grep -o '"pinned_relation":"[^"]*"' $d/rust_batch.json | head -1)" | tee -a $O/summary.txt
done
kill $(cat $O/serve.pid) 2>/dev/null
echo LIVE_DONE | tee -a $O/summary.txt
