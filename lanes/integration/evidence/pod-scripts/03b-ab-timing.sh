#!/usr/bin/env bash
# integration merge-val-3 (c, timings): clean-GPU rerun per the coordinator's 01:27Z handoff -- alternating arms, 3 rounds,
# no dumps, nothing else on the GPU (checked before every run). Same configs as the digest pairs in 03-ab.sh.
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
O=/workspace/integration/abt; mkdir -p $O; : > $O/timings.tsv
one() {  # tag, env assignment, relation, extra args...
  local tag=$1 envv=$2 rel=$3; shift 3
  local others=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)
  env $envv $PY -m backends.direct.ligero.run --relation $rel bench-vu --mode fiat-shamir --target -128 --reps 3 \
      --out $O/$tag.json "$@" > $O/$tag.log 2>&1
  local rc=$?
  echo -e "$tag\trc=$rc\tgpu_others_before=$others\t$($PY -c 'import json,sys;m={x["name"]:x["value"] for x in json.load(open(sys.argv[1]))["measurements"]};print("t.total=%.4f\tt.witness=%.4f\thints=%.4f\twitness_torch=%.4f"%(m["t.total"],m["t.witness"],m["split.hints_seconds"],m["split.witness_torch_seconds"]))' $O/$tag.json 2>&1 | tail -1)" | tee -a $O/timings.tsv
}
LV="fp8-ada --auth included-hash --leaf blake3 --total-vus 1024 --batch 4096 --pipeline 2"
FH="fp8-ada-v3x4 --total-vus 4096 --batch 4096 --pipeline 4"
for r in 1 2 3; do
  if [ $((r % 2)) = 1 ]; then o="1 0"; else o="0 1"; fi
  for a in $o; do one lv$a-blake3-r$r LIGERO_INTERP_LEVELS=$a $LV; done
  for a in $o; do one fh$a-v3x4-r$r LIGERO_FUSED_HINTS=$a $FH; done
done
echo ABT_DONE | tee -a $O/timings.tsv
