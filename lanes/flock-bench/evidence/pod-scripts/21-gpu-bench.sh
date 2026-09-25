#!/usr/bin/env bash
# flock-bench: 5090 GPU provers at verity batch points.
#  A. Flock-CUDA (succinctlabs/flock cuda-ghash, BLAKE3 only; on-device witness gen; Rust verifier on host)
#     m = 14 + log2(slots): 26 (FP8 N=64), 27 (BF16 N=64), 30 (FP8 N=1024), 31 (BF16 N=1024), 32 (FP8 N=4096), 33 (BF16 N=4096)
#  B. flock-zorch (JAX/FRX, clmad), BLAKE3 + SHA-256 goldens at the same compression counts
# env: CUDA_NBLS="12 13 16 17 18 19"  ZB3="3072 6144 49152 98304 196608 393216"  ZSHA="3200 6272 51200 100352 204800 401408"  PARTS="A B"
set -uxo pipefail
W=/workspace/flock-bench; OUT=$W/out/gpu-$(date -u +%H%MZ); mkdir -p $OUT
source $HOME/.cargo/env
[ -x /usr/bin/time ] || { apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq time; }
export PATH=/usr/local/cuda-13.3/bin:$PATH NVCC=/usr/local/cuda-13.3/bin/nvcc
nvidia-smi --query-gpu=name,driver_version,clocks.max.sm,power.limit,memory.total --format=csv | tee $OUT/gpu.txt
nvidia-smi --query-compute-apps=pid,name --format=csv | tee -a $OUT/gpu.txt
PARTS=${PARTS:-"A B"}
if [[ $PARTS == *A* ]]; then
  cd $W/flock
  for nbl in ${CUDA_NBLS:-12 13 16 17 18 19}; do
    /usr/bin/time -v cargo test -p flock-cuda-ffi --release --features gpu --test gpu_roundtrip -- --ignored --nocapture --exact gpu_roundtrip_vs$nbl \
      > $OUT/flockcuda-nbl$nbl.txt 2>&1
    echo "rc=$? nbl=$nbl"; grep -E "VSIZE|GPU proof verified|panicked|Maximum resident" $OUT/flockcuda-nbl$nbl.txt
  done
fi
if [[ $PARTS == *B* ]]; then
  cd $W/flock-zorch
  export FLOCK_ZORCH_ARTIFACTS=$W/zorch-artifacts; mkdir -p $FLOCK_ZORCH_ARTIFACTS
  export FRX_PLATFORMS=cuda,cpu FRX_ENABLE_X64=1 XLA_PYTHON_CLIENT_PREALLOCATE=false
  unset JAX_PLATFORMS JAX_ENABLE_X64
  export PYTHONPATH="python:$W/zorch"
  ptxas --version | tail -1
  for spec in ${ZSPECS:-"blake3:${ZB3:-3072 6144 49152 98304 196608 393216}" "sha2:${ZSHA:-3200 6272 51200 100352 204800 401408}"}; do
    circ=${spec%%:*}; counts=${spec#*:}
    for n in $counts; do
      g=${circ}_ligerito_golden_n$n.bin
      [ -s $FLOCK_ZORCH_ARTIFACTS/$g ] || \
        /usr/bin/time -v target/release/examples/dump_${circ}_ligerito $n $FLOCK_ZORCH_ARTIFACTS/$g > $OUT/zdump-$circ-n$n.txt 2>&1
      ls -la $FLOCK_ZORCH_ARTIFACTS/$g
      /usr/bin/time -v .venv/bin/python python/flock_zorch/testing/prove_phase_bench.py $circ --throughput --runs 3 --golden $g --json \
        > $OUT/zorch-$circ-n$n-thr.txt 2>&1
      echo "rc=$? zorch $circ n=$n"; grep -E "^\S*JSON|hashes/s|ms|Error|error|Maximum resident" $OUT/zorch-$circ-n$n-thr.txt | tail -6
      if [ $circ = blake3 ]; then
        .venv/bin/python python/flock_zorch/testing/prove_phase_bench.py blake3 --throughput --runs 3 --golden $g --seed 42 --json \
          > $OUT/zorch-$circ-n$n-seed.txt 2>&1
        echo "rc=$? zorch-seed n=$n"; tail -4 $OUT/zorch-$circ-n$n-seed.txt
      fi
      .venv/bin/python python/flock_zorch/testing/prove_phase_bench.py $circ --runs 2 --golden $g > $OUT/zorch-$circ-n$n-phases.txt 2>&1
      [ $n -ge 196608 ] && rm -f $FLOCK_ZORCH_ARTIFACTS/$g
    done
  done
fi
cp -r $OUT "$RESEARCH_RUN_DIR/out" 2>/dev/null || true
