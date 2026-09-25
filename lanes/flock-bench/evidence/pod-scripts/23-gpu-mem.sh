#!/usr/bin/env bash
# flock-bench: device-memory high-water of the N=4096 Flock-CUDA points (BLAKE3 m32/m33, unit m31/m32).
# Reuses the gpu_unit / gpu_roundtrip test binaries and netlists built by 21/22 (no rebuild).
set -uxo pipefail
W=/workspace/flock-bench; F=$W/flock; OUT=$W/out/gpumem-$(date -u +%H%MZ); mkdir -p $OUT
NETS=${NETS:-$W/out/gpuunit-0919Z}
source $HOME/.cargo/env
export PATH=/usr/local/cuda-13.3/bin:$PATH NVCC=/usr/local/cuda-13.3/bin/nvcc
cd $F
mem() {  # tag test-binary-name test-name [env...]
  local tag=$1 bin=$2 t=$3; shift 3
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -lms 20 > $OUT/$tag.smi &
  local sp=$!
  sleep 1
  env "$@" cargo test -p flock-cuda-ffi --release --features gpu --test $bin -- --ignored --nocapture --exact $t \
    > $OUT/$tag.txt 2>&1
  local rc=$?
  sleep 1; kill $sp
  local base; base=$(head -1 $OUT/$tag.smi)
  echo "MEM $tag rc=$rc baseline_mib=$base peak_mib=$(sort -n $OUT/$tag.smi | tail -1) samples=$(wc -l < $OUT/$tag.smi)" | tee -a $OUT/mem.txt
  grep -E "VSIZE" $OUT/$tag.txt
}
mem blake3-m32 gpu_roundtrip gpu_roundtrip_vs18
mem blake3-m33 gpu_roundtrip gpu_roundtrip_vs19
mem unit-ampere-m32 gpu_unit gpu_unit_nbl19 VU_NETLIST=$NETS/net-ampere_bf16.txt VU_NAME=ampere_bf16
mem unit-ada-m31 gpu_unit gpu_unit_nbl18 VU_NETLIST=$NETS/net-ada_e4m3.txt VU_NAME=ada_e4m3
cp -r $OUT "$RESEARCH_RUN_DIR/out" 2>/dev/null || true
