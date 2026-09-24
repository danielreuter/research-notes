#!/bin/bash
# hints-fused-2 chain3 (tree e57637f content): the H100 headline families on the 4090, fused vs torch hint path, 2 rounds.
cd /workspace
B="/workspace/venv312/bin/python -m backends.direct.ligero.run"
C="--zk --mode interactive --reps 3 --device cuda --instances-cache /workspace/instances-cache"
X=/workspace/src
L=/workspace/logs/chain3.log
mkdir -p /workspace/results3
run() {  # run TAG FUSED REL BATCH PIPE
  local tag=$1 fu=$2 rel=$3 bt=$4 pp=$5; shift 5
  LIGERO_FUSED_HINTS=$fu LIGERO_REFERENCE_HINTS=0 /workspace/run.sh $X $tag $B --relation $rel bench-vu $C --total-vus 4096 \
    --batch $bt --pipeline $pp --out /workspace/results3/$tag.json "$@"
  echo "$(date -u +%H:%M:%S) $tag rc=$(grep -o 'rc=[0-9]*' /workspace/logs/$tag.log | tail -1)" >> $L
}
echo "chain3 start $(date -u +%H:%M:%S)" > $L
for r in 6 7; do
  run r${r}_to_bf16h-v3_p4_16k   0 bf16-hopper-v3   16384 4
  run r${r}_fu_bf16h-v3_p4_16k   1 bf16-hopper-v3   16384 4
  run r${r}_fu_bf16h-v3x4_p4_4k  1 bf16-hopper-v3x4 4096  4
  run r${r}_to_bf16h-v3x4_p4_4k  0 bf16-hopper-v3x4 4096  4
  run r${r}_to_fp8h-v3_p4_16k    0 fp8-hopper-v3    16384 4
  run r${r}_fu_fp8h-v3_p4_16k    1 fp8-hopper-v3    16384 4
  run r${r}_fu_fp8h-v3x4_p4_4k   1 fp8-hopper-v3x4  4096  4
  run r${r}_to_fp8h-v3x4_p4_4k   0 fp8-hopper-v3x4  4096  4
done
echo CHAIN3_DONE >> $L
