#!/usr/bin/env bash
# integration merge-val-3 (b): gates at 4096 VUs, local coins, zk interactive, --batch 16384; one log + --out JSON per cell
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
O=/workspace/integration/gates; mkdir -p $O
run() {  # name, relation, extra args...
  local name=$1 rel=$2; shift 2
  local t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel gate-vu --vus 4096 --batch 16384 --zk --mode interactive \
      --out $O/$name.json "$@" > $O/$name.log 2>&1
  local rc=$?
  echo "$name rc=$rc $(( $(date +%s) - t0 ))s :: $(grep -E 'gate: .* failures' $O/$name.log | tail -1)" | tee -a $O/summary.txt
}
for rel in fp8-ada bf16-hopper bf16-ampere fp8-hopper; do
  run $rel-bare $rel
  run $rel-hash $rel --auth included-hash
  run $rel-shared $rel --auth included-hash-shared --tile 64x64
done
run fp8-ada-v3-bare fp8-ada-v3
run fp8-ada-v3x4-bare fp8-ada-v3x4 --batch 4096
echo GATES_DONE | tee -a $O/summary.txt
