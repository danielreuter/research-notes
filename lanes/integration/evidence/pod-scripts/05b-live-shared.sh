#!/usr/bin/env bash
# integration merge-val-3 (e): live verifier on THIS pod (localhost, merged tree) + one live --zk interactive session each for
# fp8-ada bare and +shared (tile 64x64); Rust batch re-verifies every session dir
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
# rerun of the +shared session alone: in 05-live.sh it hit CUDA OOM beside the v3/v3x4 gates (~7 GB); GPU otherwise idle now
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
O=/workspace/integration/live; rm -f $O/summary2.txt; mkdir -p $O/sessions
setsid nohup $PY -m backends.direct.ligero.live serve --listen 127.0.0.1:7000 --out $O/sessions --jobs 4 --threads 1 \
  --target-bits 128 > $O/serve.out 2>&1 < /dev/null &
echo $! > $O/serve.pid
sleep 8
lv() {  # tag, relation, extra args...
  local tag=$1 rel=$2; shift 2
  rm -rf $O/$tag; mkdir -p $O/$tag
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch 16384 --pipeline 4 \
      --total-vus 4096 --target -128 --reps 1 --verifier tcp://127.0.0.1:7000 --out $O/$tag/result.json "$@" > $O/$tag/log 2>&1
  echo "$tag bench rc=$?" | tee -a $O/summary2.txt
}
# (bare session done in 05-live.sh: s20260924T020140Z-2ca7)
lv fp8-ada-shared fp8-ada --auth included-hash-shared --tile 64x64
sleep 5
cp $O/sessions/index.jsonl $O/index.jsonl 2>/dev/null
for d in $O/sessions/s*/; do
  [ -f $d/system.bin ] || continue
  hs=""; [ -f $d/system_h.bin ] && hs="--system-h system_h.bin"
  ( cd $d && $LIGERO_VERIFY batch --system system.bin $hs --dir . --jobs 8 --threads 1 --target-bits 128 \
      --json rust_rebatch.json > rust_rebatch.out 2> rust_rebatch.err )
  echo "$(basename $d) rust rc=$? $($PY -c 'import json,sys;x=json.load(open(sys.argv[1]));print("accepted",x["accepted"],"/",x["n"],"own_coins",x.get("own_coins"),"batch",x["batch_accepted"],"bits %.2f"%x["batch_bits"],"pinned",x["system_pinned"],x["system"]["pinned_relation"])' $d/rust_rebatch.json 2>&1 | tail -1) verdict=$(cat $d/verdict.json 2>/dev/null | tr -d '\n' | cut -c1-160)" | tee -a $O/summary2.txt
done
kill $(cat $O/serve.pid) 2>/dev/null
echo LIVE_DONE | tee -a $O/summary2.txt
