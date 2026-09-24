#!/usr/bin/env bash
# integration merge-val-3 (c): the rest of 03-ab.sh's digest pairs (its v3x4 arm stalled under the 10.2-core CPU quota and was
# killed; blake3 pair + probe already done there). Digests only -- timings are 03b-ab-timing.sh on a clean GPU.
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
O=/workspace/integration/ab; mkdir -p $O
ab() {  # tag, env assignment, relation, extra args...
  local tag=$1 envv=$2 rel=$3; shift 3
  rm -rf $O/$tag; mkdir -p $O/$tag
  env $envv $PY -m backends.direct.ligero.run --relation $rel bench-vu --mode fiat-shamir --target -128 \
      --reps 3 --dump-dir $O/$tag/dump --dump-reps 1 --out $O/$tag/result.json "$@" > $O/$tag/log 2>&1
  echo "$tag rc=$? $(grep -o '"total": [0-9.]*' $O/$tag/result.json | head -1)" | tee -a $O/summary.txt
  ( cd $O/$tag/dump && find . -name '*.stmt' -o -name '*.proof' -o -name 'system*.bin' | sort | xargs sha256sum ) > $O/$tag/digests.txt
}
# LIGERO_INTERP_LEVELS: the +blake3 system is the one that takes the interpreter (probe above)
# the coordinator's ask: v3x4 fused l=4096 p4 and v1 p4 with levels on / off
ab lv1-v3x4 LIGERO_INTERP_LEVELS=1 fp8-ada-v3x4 --total-vus 4096 --batch 4096 --pipeline 4
ab lv0-v3x4 LIGERO_INTERP_LEVELS=0 fp8-ada-v3x4 --total-vus 4096 --batch 4096 --pipeline 4
ab lv1-v1 LIGERO_INTERP_LEVELS=1 fp8-ada --total-vus 4096 --batch 16384 --pipeline 4
ab lv0-v1 LIGERO_INTERP_LEVELS=0 fp8-ada --total-vus 4096 --batch 16384 --pipeline 4
# LIGERO_FUSED_HINTS on the fused v3x4 relation
ab fh1-v3x4 LIGERO_FUSED_HINTS=1 fp8-ada-v3x4 --total-vus 4096 --batch 4096 --pipeline 4
ab fh0-v3x4 LIGERO_FUSED_HINTS=0 fp8-ada-v3x4 --total-vus 4096 --batch 4096 --pipeline 4
for p in "lv1-blake3 lv0-blake3" "lv1-v3x4 lv0-v3x4" "lv1-v1 lv0-v1" "fh1-v3x4 fh0-v3x4"; do
  set -- $p
  if [ -s $O/$1/digests.txt ] && cmp -s $O/$1/digests.txt $O/$2/digests.txt; then v=IDENTICAL; else v=DIFFER; fi
  echo "$1 vs $2: $v ($(wc -l < $O/$1/digests.txt) files, combined $(sha256sum $O/$1/digests.txt | cut -c1-16))" | tee -a $O/summary.txt
done
echo AB_DONE | tee -a $O/summary.txt
