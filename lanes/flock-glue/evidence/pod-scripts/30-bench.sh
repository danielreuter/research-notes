#!/usr/bin/env bash
# flock-glue: end-to-end binary backend per VU batch = census unit proof + BLAKE3 row-leaf proof (two Flock-CUDA
# proofs, every one verified outside the timed region). Variants per (pipe, VUs):
#   before  = mode 1: host-built unit witness (flock-bench tiled vectors) + 2.1 GB pageable upload, host PoW grinding
#   devwit  = mode 2: unit witness built on the device from resident operand rows, host PoW grinding
#   devgpu  = mode 2 + FLOCK_GLUE_GPU_GRIND=1 (Fiat-Shamir PoW searched on the GPU)
# then one diagnostic phase-timer run per mode (FLOCK_GLUE_PHASES=1, syncs at each phase: not a timing run).
# Flock profile: b684b12 default (Fast Ligerito, SHA-256 FS + Merkle, GF(2^128), "strict 128" = 16-bit PoW credit;
# about 2^-100 under campaign accounting, red-team-link §3).
# env: PIPES="ampere_bf16" NVUS="1024 4096" VARIANTS="before devwit devgpu" REPS=5 PHASES=1
set -uxo pipefail
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
W=/workspace/flock-glue; F=$W/flock
export LD_LIBRARY_PATH=/usr/local/cuda-13.3/lib64:${LD_LIBRARY_PATH:-}
Q=$(awk '{ if ($1 != "max") printf "%d", $1 / $2; else print 16 }' /sys/fs/cgroup/cpu.max 2>/dev/null || echo 16)
export RAYON_NUM_THREADS=${RAYON_NUM_THREADS:-$Q}
BIN=$(ls -t $F/target/release/deps/gpu_glue-* | grep -v '\.d$' | head -1)
OUT=${RESEARCH_RUN_DIR:-$W/out}/bench; mkdir -p $OUT
nvidia-smi --query-gpu=name,driver_version,clocks.max.sm,power.limit,memory.total --format=csv | tee $OUT/gpu.txt
lscpu | grep 'Model name' | tee -a $OUT/gpu.txt; echo "rayon=$RAYON_NUM_THREADS" | tee -a $OUT/gpu.txt
cd $F/crates/flock-cuda-ffi
b3nbl() {  # pipe nvu -> log2(BLAKE3 compressions): 96 / 48 per VU
  case $1 in *bf16) c=$(( $2 * 96 ));; *) c=$(( $2 * 48 ));; esac
  n=0; while [ $(( 1 << n )) -lt $c ]; do n=$((n + 1)); done; echo $n
}
unbl() {  # pipe nvu -> unit nbl (m = 13 + nbl); FP8 1024 VUs is m29, which has no Flock-CUDA config: pad to m30
  case $1 in *bf16) c=$(( $2 * 96 ));; *) c=$(( $2 * 48 ));; esac
  n=0; while [ $(( 1 << n )) -lt $c ]; do n=$((n + 1)); done
  [ $((13 + n)) = 29 ] && n=17; echo $n
}
run() {  # tag pipe nvu mode reps [env...]
  local tag=$1 pipe=$2 nvu=$3 mode=$4 reps=$5; shift 5
  env "$@" VU_NETLIST=$W/net/net-$pipe.txt VU_NAME=$pipe VU_NVU=$nvu GLUE_MODE=$mode GLUE_REPS=$reps \
    GLUE_B3_NBL=$(b3nbl $pipe $nvu) GLUE_UNIT_NBL=$(unbl $pipe $nvu) \
    /usr/bin/time -v $BIN --ignored --nocapture --exact glue_bench > $OUT/$tag.txt 2>&1
  echo "rc=$? $tag"; grep -E "VWIT|VSUMMARY|REJECTED|panicked|Maximum resident" $OUT/$tag.txt | head -8
}
for pipe in ${PIPES:-ampere_bf16}; do
  for nvu in ${NVUS:-1024 4096}; do
    for v in ${VARIANTS:-before devwit devgpu}; do
      case $v in
        before) run $pipe-$nvu-before $pipe $nvu 1 ${REPS:-5};;
        devwit) run $pipe-$nvu-devwit $pipe $nvu 2 ${REPS:-5};;
        devgpu) run $pipe-$nvu-devgpu $pipe $nvu 2 ${REPS:-5} FLOCK_GLUE_GPU_GRIND=1;;
      esac
    done
    if [ "${PHASES:-1}" = 1 ]; then
      run $pipe-$nvu-phases-before $pipe $nvu 1 1 FLOCK_GLUE_PHASES=1
      run $pipe-$nvu-phases-devgpu $pipe $nvu 2 1 FLOCK_GLUE_PHASES=1 FLOCK_GLUE_GPU_GRIND=1
    fi
  done
done
grep -h VSUMMARY $OUT/*.txt | tee $OUT/summary.txt
