#!/usr/bin/env bash
# commit-gpu (survey §4.1): Flock cuda-ghash test_f128 / clmad_peak / bench_f128, AOT-built with CUDA 13.3.1 (80-flock-setup.sh)
# for ARCH (sm_89 4090, sm_90 H100), on an idle GPU; outputs + SASS CLMAD counts under $HC/flock/<arch>/, one line to runs.txt
source /workspace/hash-commit/scripts/lib.sh
ARCH=${ARCH:-sm_89}; B=/workspace/flock-bin/$ARCH; D=$HC/flock/$ARCH; mkdir -p $B $D
export PATH=/workspace/cuda-13.3/bin:$PATH
cd /workspace/flock/cuda-ghash
for t in clmad_peak bench_f128 test_f128; do
  [ -x $B/$t ] || nvcc -O3 -gencode arch=compute_${ARCH#sm_},code=$ARCH -lineinfo -std=c++17 $t.cu -o $B/$t
  echo "$t $(cuobjdump -sass $B/$t | grep -c CLMAD)" >> $D/sass_clmad_counts.txt
done
( nvidia-smi --query-gpu=name,driver_version,clocks.max.sm,clocks.sm --format=csv; nvcc --version | tail -2
  git -C /workspace/flock log -1 --format='flock %H %cd' ) > $D/env.txt
gpu_idle || exit 1
$B/test_f128 > $D/test_f128.txt 2>&1; rt=$?
$B/clmad_peak > $D/clmad_peak.txt 2>&1; rp=$?
$B/bench_f128 > $D/bench_f128.txt 2>&1; rb=$?
echo "$(date -u +%H:%M:%SZ) flock $ARCH test=$rt peak=$rp bench=$rb $(grep -h 'CLMAD peak' $D/clmad_peak.txt | tr -s ' ' | cut -c1-160)" | tee -a $LOG
