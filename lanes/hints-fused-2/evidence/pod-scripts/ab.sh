#!/bin/bash
# A/B on the lane tree: LIGERO_FUSED_HINTS=1 (fused kernel) vs 0 (the torch graph path == 5e6b3e3's hint code), interleaved.
# Round 0 (evidence): fused v3x4 p2 with the warm-up's Python-reference comparison ON + dumps + Rust batch verify.
cd /workspace
B="/workspace/venv312/bin/python -m backends.direct.ligero.run"
C="--zk --mode interactive --reps 3 --device cuda --instances-cache /workspace/instances-cache"
X=/workspace/src
run() {  # run TAG FUSED REL BATCH PIPE VUS [extra...]
  local tag=$1 fu=$2 rel=$3 bt=$4 pp=$5 nv=$6; shift 6
  LIGERO_FUSED_HINTS=$fu LIGERO_REFERENCE_HINTS=${REF:-0} /workspace/run.sh $X $tag $B --relation $rel bench-vu $C --total-vus $nv --batch $bt --pipeline $pp --out /workspace/results/$tag.json "$@"
}
rust() {  # rust TAG
  /workspace/bin/ligero-verify batch --system /workspace/dumps/$1/system.bin --dir /workspace/dumps/$1/rep1 --target-bits 128 > /workspace/logs/$1_rust.log 2>&1
  echo "rc=$?" >> /workspace/logs/$1_rust.log
}
REF=1 run ab0_fu_v3x4_p2_16k 1 fp8-ada-v3x4 16384 2 4096 --dump-dir /workspace/dumps/ab0_fu_v3x4_p2_16k --dump-reps 1; rust ab0_fu_v3x4_p2_16k
for r in 1 2; do
  run ab${r}_fu_v3x4_p4_16k 1 fp8-ada-v3x4 16384 4 4096
  run ab${r}_to_v3_p4_16k   0 fp8-ada-v3   16384 4 4096
  run ab${r}_fu_v3x4_p2_16k 1 fp8-ada-v3x4 16384 2 4096
  run ab${r}_to_v3x4_p2_16k 0 fp8-ada-v3x4 16384 2 4096
  run ab${r}_fu_v3_p4_16k   1 fp8-ada-v3   16384 4 4096
  run ab${r}_to_v3x4_p4_16k 0 fp8-ada-v3x4 16384 4 4096
done
run ab1_fu_v3x4_p4_16k_dump 1 fp8-ada-v3x4 16384 4 4096 --dump-dir /workspace/dumps/ab1_fu_v3x4_p4_16k_dump --dump-reps 1; rust ab1_fu_v3x4_p4_16k_dump
run ab1_fu_v3x4_p4_4k  1 fp8-ada-v3x4 4096 4 4096
run ab1_to_v3x4_p4_4k  0 fp8-ada-v3x4 4096 4 4096
run ab1_fu_v2x4_p4_16k 1 fp8-ada-v2x4 16384 4 4096
run ab1_to_v2x4_p4_16k 0 fp8-ada-v2x4 16384 4 4096
run ab1_fu_v3x4_p2_16k_4095 1 fp8-ada-v3x4 16384 2 4095
run ab1_fu_v3x4_p4_16k_4095 1 fp8-ada-v3x4 16384 4 4095
echo AB_DONE > /workspace/logs/ab_done
