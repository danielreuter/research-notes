#!/usr/bin/env bash
# flock-128: Flock-CUDA (b684b12, sm_90) on one H100 under today's profile (fast x1) and flock-128-r2 (fast100 x2).
# Setup = flock-bench-80gb 00-setup.sh (CUDA 13.3 + compat, rust, clone) minus clmad/CPU bench; build.rs sed as its
# 20-gpu.sh; then evidence/pod-scripts/g128_patch.py on tests/gpu_roundtrip.rs, then flock-bench's 22-gpu-unit.sh
# (shipped unchanged with an fb_ prefix, BUILD_ONLY=1) generates + builds tests/gpu_unit.rs from the patched file.
# Shapes (as flock-bench-80gb): BLAKE3 nbl 19/18 (BF16/FP8 4096 VUs), 17/16 (1024); unit hopper_bf16 19 (4096) 17 (1024),
# hopper_e4m3 18 (4096) 17 (1024, padded: no config at m29). env: ROUNDS=2 GPU_RUNS=3 PROFILES="fast:1 fast100:2" SM=90
set -uxo pipefail
SM=${SM:-90}; FLOCK_REV=${FLOCK_REV:-b684b12}
W=/workspace/flock-bench; F=$W/flock; O=/workspace/flock-128/out/gpu128-$(date -u +%H%MZ); mkdir -p $W $O
I=$RESEARCH_RUN_DIR/inputs
nvidia-smi; nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; free -g
C13=/usr/local/cuda-13.3
if [ ! -x $C13/bin/nvcc ]; then
  export DEBIAN_FRONTEND=noninteractive
  . /etc/os-release; REPO=ubuntu${VERSION_ID/./}
  dpkg -s cuda-keyring >/dev/null 2>&1 || { wget -q https://developer.download.nvidia.com/compute/cuda/repos/$REPO/x86_64/cuda-keyring_1.1-1_all.deb && dpkg -i cuda-keyring_1.1-1_all.deb; }
  apt-get update -qq
  apt-get install -y -qq --no-install-recommends cuda-toolkit-13-3 || exit 1
fi
[ -x /usr/bin/time ] || apt-get install -y -qq time
DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | cut -d. -f1)
[ "$DRV" -lt 580 ] && { DEBIAN_FRONTEND=noninteractive apt-get install -y -qq cuda-compat-13-3 || exit 1; }
export PATH=$C13/bin:$PATH NVCC=$C13/bin/nvcc LD_LIBRARY_PATH=$C13/compat:$C13/lib64:${LD_LIBRARY_PATH:-}
command -v cargo >/dev/null || [ -x $HOME/.cargo/bin/cargo ] || curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable
source $HOME/.cargo/env; rustc --version
cd $W; [ -d flock ] || git clone -q https://github.com/succinctlabs/flock
cd $F && git checkout -q $FLOCK_REV && git log --oneline -1
git checkout -q crates/flock-cuda-ffi cuda-ghash
sed -i "s/arch=compute_120,code=sm_120/arch=compute_$SM,code=sm_$SM/; s#/usr/local/cuda/lib64#$C13/lib64#g" crates/flock-cuda-ffi/build.rs
python3 $I/g128_patch.py || exit 1
mkdir -p $RESEARCH_RUN_DIR/fb/inputs
for f in $I/fb_*; do cp $f $RESEARCH_RUN_DIR/fb/inputs/$(basename $f | sed 's/^fb_//'); done
RESEARCH_RUN_DIR=$RESEARCH_RUN_DIR/fb BUILD_ONLY=1 bash $RESEARCH_RUN_DIR/fb/inputs/22-gpu-unit.sh || exit 1
NETS=$(ls -td $W/out/gpuunit-* | head -1)
cargo test -p flock-cuda-ffi --release --features gpu --test gpu_roundtrip --no-run > $O/build-roundtrip.txt 2>&1 || { tail -40 $O/build-roundtrip.txt; exit 1; }
(cd $F && git diff -- crates/flock-cuda-ffi cuda-ghash; git status --short) > $O/flock-cuda-128.diff
nvidia-smi --query-gpu=name,driver_version,memory.total,clocks.max.sm --format=csv | tee $O/gpu.txt
[ "${BUILD_ONLY:-0}" = 1 ] && { cp -r $O $RESEARCH_RUN_DIR/out; exit 0; }
t() {  # test-binary tag pipe(or -) nbl [env...]
  local bin=$1 tag=$2 pipe=$3; shift 3
  local extra=(); [ "$pipe" != - ] && extra=(VU_NETLIST=$NETS/net-$pipe.txt VU_NAME=$pipe)
  local f=$O/$tag-${pipe}-${GPU_PROFILE}x${GPU_REPS}-${RTAG}.txt
  env "${extra[@]}" "$@" GPU_PROFILE=$GPU_PROFILE GPU_REPS=$GPU_REPS /usr/bin/time -v \
    cargo test -p flock-cuda-ffi --release --features gpu --test $bin -- --ignored --nocapture --exact $tag > $f 2>&1
  echo "rc=$? $tag $pipe $GPU_PROFILE x$GPU_REPS $RTAG"; grep -hE "G128RESULT|G128NEG|panicked|Maximum resident" $f | cut -c1-500
}
# negatives first, both profiles: proof/transcript tampers (GPU_NEG) and a witness tamper (VU_TAMPER_W, must reject)
for pr in ${PROFILES:-fast:1 fast100:2}; do
  GPU_PROFILE=${pr%:*} GPU_REPS=${pr#*:} RTAG=neg t gpu_unit gpu_unit_nbl17 hopper_bf16 GPU_RUNS=1 GPU_NEG=1
  GPU_PROFILE=${pr%:*} GPU_REPS=${pr#*:} RTAG=negw t gpu_unit gpu_unit_nbl17 hopper_bf16 GPU_RUNS=1 VU_TAMPER_W=1 EXPECT_REJECT=1
  GPU_PROFILE=${pr%:*} GPU_REPS=${pr#*:} RTAG=neg t gpu_roundtrip gpu_roundtrip_vs17 - GPU_RUNS=1 GPU_NEG=1
done
for r in $(seq 1 ${ROUNDS:-2}); do
  for pr in ${PROFILES:-fast:1 fast100:2}; do
    export GPU_PROFILE=${pr%:*} GPU_REPS=${pr#*:} RTAG=r$r GPU_RUNS=${GPU_RUNS:-3}
    for nbl in 19 18 17 16; do t gpu_roundtrip gpu_roundtrip_vs$nbl -; done
    t gpu_unit gpu_unit_nbl19 hopper_bf16; t gpu_unit gpu_unit_nbl17 hopper_bf16
    t gpu_unit gpu_unit_nbl18 hopper_e4m3; t gpu_unit gpu_unit_nbl17 hopper_e4m3
  done
done
grep -h G128RESULT $O/*.txt | sed 's/^G128RESULT\t\?//' > $O/results.jsonl
grep -h G128NEG $O/*.txt > $O/negatives.txt
cp -r $O $RESEARCH_RUN_DIR/out
