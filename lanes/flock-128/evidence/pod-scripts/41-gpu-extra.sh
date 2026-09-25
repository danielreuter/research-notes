#!/usr/bin/env bash
# flock-128: decomposition runs on the tree 40-gpu128.sh built (no rebuild): fast100 x1 (no second rep) and fast x2
# (grinding kept, two reps) at the 4096-VU shapes, so the fast x1 -> fast100 x2 ratio splits into grinding and repetition.
# env: PROFILES="fast100:1 fast:2" GPU_RUNS=3
set -uxo pipefail
F=/workspace/flock-bench/flock; O=/workspace/flock-128/out/gpu128x-$(date -u +%H%MZ); mkdir -p $O
C13=/usr/local/cuda-13.3; export PATH=$C13/bin:$PATH NVCC=$C13/bin/nvcc LD_LIBRARY_PATH=$C13/compat:$C13/lib64:${LD_LIBRARY_PATH:-}
source $HOME/.cargo/env; cd $F
NETS=$(ls -td /workspace/flock-bench/out/gpuunit-* | head -1)
t() {
  local bin=$1 tag=$2 pipe=$3; shift 3
  local extra=(); [ "$pipe" != - ] && extra=(VU_NETLIST=$NETS/net-$pipe.txt VU_NAME=$pipe)
  local f=$O/$tag-${pipe}-${GPU_PROFILE}x${GPU_REPS}.txt
  env "${extra[@]}" "$@" GPU_PROFILE=$GPU_PROFILE GPU_REPS=$GPU_REPS GPU_RUNS=${GPU_RUNS:-3} /usr/bin/time -v \
    cargo test -p flock-cuda-ffi --release --features gpu --test $bin -- --ignored --nocapture --exact $tag > $f 2>&1
  echo "rc=$? $tag $pipe $GPU_PROFILE x$GPU_REPS"; grep -hE "G128RESULT|panicked" $f | cut -c1-400
}
for pr in ${PROFILES:-fast100:1 fast:2}; do
  export GPU_PROFILE=${pr%:*} GPU_REPS=${pr#*:}
  t gpu_roundtrip gpu_roundtrip_vs19 -; t gpu_roundtrip gpu_roundtrip_vs18 -
  t gpu_unit gpu_unit_nbl19 hopper_bf16; t gpu_unit gpu_unit_nbl18 hopper_e4m3
done
grep -h G128RESULT $O/*.txt | sed 's/^G128RESULT //' > $O/results.jsonl
cp -r $O $RESEARCH_RUN_DIR/out
