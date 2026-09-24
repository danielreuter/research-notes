#!/usr/bin/env bash
# integration merge-val-3 (c): byte-identity A/B (deterministic: fiat-shamir, no --zk) + timings; interpreter-path probe
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
O=/workspace/integration/ab; mkdir -p $O
$PY - > $O/interp_probe.txt 2>&1 <<'EOF'
from backends.direct.ligero import witness_device as wd, hashchain
from backends.direct.ligero.relations import relation
print("INTERP_OPS", wd.INTERP_OPS, "INTERP_LEVELS", wd.INTERP_LEVELS)
for name in ["fp8-ada", "bf16-hopper", "fp8-ada-v3", "fp8-ada-v3x4", "bf16-hopper-v3x4"]:
    r = relation(name); n = len(wd._program(r.compile(r.params, True)))
    print(f"{name:20s} bare     ops={n:7d} interpreter={n > wd.INTERP_OPS}")
for name, leaf in [("fp8-ada", "poseidon2"), ("fp8-ada", "ajtai-n64"), ("fp8-ada", "blake3"), ("fp8-ada-v3x4", "poseidon2")]:
    try:
        n = len(wd._program(hashchain.compose(relation(name), leaf).sys))
        print(f"{name:20s} +{leaf:9s} ops={n:7d} interpreter={n > wd.INTERP_OPS}")
    except Exception as e:
        print(f"{name} +{leaf}: {type(e).__name__}: {e}")
EOF
ab() {  # tag, env assignment, relation, extra args...
  local tag=$1 envv=$2 rel=$3; shift 3
  rm -rf $O/$tag; mkdir -p $O/$tag
  env $envv $PY -m backends.direct.ligero.run --relation $rel bench-vu --mode fiat-shamir --target -128 \
      --reps 3 --dump-dir $O/$tag/dump --dump-reps 1 --out $O/$tag/result.json "$@" > $O/$tag/log 2>&1
  echo "$tag rc=$? $(grep -o '"total": [0-9.]*' $O/$tag/result.json | head -1)" | tee -a $O/summary.txt
  ( cd $O/$tag/dump && find . -name '*.stmt' -o -name '*.proof' -o -name 'system*.bin' | sort | xargs sha256sum ) > $O/$tag/digests.txt
}
# LIGERO_INTERP_LEVELS: the +blake3 system is the one that takes the interpreter (probe above)
ab lv1-blake3 LIGERO_INTERP_LEVELS=1 fp8-ada --auth included-hash --leaf blake3 --total-vus 1024 --batch 4096 --pipeline 2
ab lv0-blake3 LIGERO_INTERP_LEVELS=0 fp8-ada --auth included-hash --leaf blake3 --total-vus 1024 --batch 4096 --pipeline 2
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
