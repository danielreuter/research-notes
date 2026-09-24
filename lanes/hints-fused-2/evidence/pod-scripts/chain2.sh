#!/bin/bash
# hints-fused-2 chain (tree 6caa2f5 = ff52e47 + test param): 3 interleaved bench rounds, dumps + Rust at the floor configs,
# profiles, extended differential.  4096 VUs, --zk --mode interactive, local coins, 3 reps per run; LIGERO_REFERENCE_HINTS=0.
cd /workspace
B="/workspace/venv312/bin/python -m backends.direct.ligero.run"
C="--zk --mode interactive --reps 3 --device cuda --instances-cache /workspace/instances-cache"
X=/workspace/src
L=/workspace/logs/chain2.log
mkdir -p /workspace/results2 /workspace/dumps2 /workspace/prof2
run() {  # run TAG FUSED TREE REL BATCH PIPE [extra...]
  local tag=$1 fu=$2 tree=$3 rel=$4 bt=$5 pp=$6; shift 6
  LIGERO_FUSED_HINTS=$fu LIGERO_REFERENCE_HINTS=0 /workspace/run.sh $tree $tag $B --relation $rel bench-vu $C --total-vus 4096 \
    --batch $bt --pipeline $pp --out /workspace/results2/$tag.json "$@"
  echo "$(date -u +%H:%M:%S) $tag rc=$(grep -o 'rc=[0-9]*' /workspace/logs/$tag.log | tail -1)" >> $L
}
rust() {  # rust TAG
  /workspace/bin/ligero-verify batch --system /workspace/dumps2/$1/system.bin --dir /workspace/dumps2/$1/rep1 --target-bits 128 \
    > /workspace/logs/$1_rust.log 2>&1
  echo "rc=$?" >> /workspace/logs/$1_rust.log
  echo "$(date -u +%H:%M:%S) $1 rust $(grep -o 'batch ACCEPT\|batch REJECT' /workspace/logs/$1_rust.log | head -1)" >> $L
}
echo "chain2 start $(date -u +%H:%M:%S)" > $L
for r in 3 4 5; do
  run r${r}_to_v3_p4_16k     0 $X fp8-ada-v3   16384 4
  run r${r}_fu_v3x4_p4_4k    1 $X fp8-ada-v3x4 4096  4
  run r${r}_fu_v3_p4_16k     1 $X fp8-ada-v3   16384 4
  run r${r}_fu_v3x4_p4_16k   1 $X fp8-ada-v3x4 16384 4
  run r${r}_to_v3x4_p4_4k    0 $X fp8-ada-v3x4 4096  4
  run r${r}_fu_v3x4_p2_16k   1 $X fp8-ada-v3x4 16384 2
  run r${r}_fu_v3x4_p4_8k    1 $X fp8-ada-v3x4 8192  4
  run r${r}_to_v3x4_p2_16k   0 $X fp8-ada-v3x4 16384 2
  run r${r}_fu_v3x4_p2_8k    1 $X fp8-ada-v3x4 8192  2
  run r${r}_fu_v3x4_p8_4k    1 $X fp8-ada-v3x4 4096  8
  run r${r}_base_v3_p4_16k   0 /workspace/src-base fp8-ada-v3 16384 4
  run r${r}_fu_v2x4_p4_16k   1 $X fp8-ada-v2x4 16384 4
  run r${r}_to_v2x4_p4_16k   0 $X fp8-ada-v2x4 16384 4
done
echo "rounds done $(date -u +%H:%M:%S)" >> $L
for t in "d_fu_v3x4_p4_4k 1 fp8-ada-v3x4 4096 4" "d_fu_v3_p4_16k 1 fp8-ada-v3 16384 4" "d_fu_v2x4_p4_16k 1 fp8-ada-v2x4 16384 4" \
         "d_fu_v3x4_p8_4k 1 fp8-ada-v3x4 4096 8"; do
  set -- $t
  run $1 $2 $X $3 $4 $5 --dump-dir /workspace/dumps2/$1 --dump-reps 1
  rust $1
done
P="/workspace/venv312/bin/python prof_rep.py"
PC="--zk --mode interactive --reps 2 --device cuda --instances-cache /workspace/instances-cache --total-vus 4096"
LIGERO_REFERENCE_HINTS=0 /workspace/run.sh $X prof_fu_v3x4_p4_4k $P /workspace/prof2/fu_v3x4_p4_4k --relation fp8-ada-v3x4 bench-vu \
  --out /workspace/results2/prof_fu_v3x4_p4_4k.json $PC --batch 4096 --pipeline 4
LIGERO_REFERENCE_HINTS=0 /workspace/run.sh $X prof_fu_v3_p4_16k $P /workspace/prof2/fu_v3_p4_16k --relation fp8-ada-v3 bench-vu \
  --out /workspace/results2/prof_fu_v3_p4_16k.json $PC --batch 16384 --pipeline 4
echo "prof done $(date -u +%H:%M:%S)" >> $L
HINTS_FUSED_N=131072 OMP_NUM_THREADS=4 LIGERO_INSTANCES_CACHE=/workspace/instances-cache /workspace/run.sh $X diff_ext \
  /workspace/venv312/bin/python -m pytest -q -rfE -p no:cacheprovider --durations=10 backends/direct/ligero/hints_fused_test.py
echo "diff done $(date -u +%H:%M:%S)" >> $L
echo CHAIN2_DONE > /workspace/logs/chain2_done
