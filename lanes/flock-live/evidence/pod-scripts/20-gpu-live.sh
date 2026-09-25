#!/usr/bin/env bash
# flock-live R6: Flock-CUDA (b684b12, sm_90) on one H100, flock-128-r2 (fast100 x2) with live verifier coins against
# Fiat-Shamir, same pod, alternating. Setup = flock-128's 40-gpu128.sh (CUDA 13.3, g128_patch.py, flock-bench's
# 22-gpu-unit.sh shipped as fb_*) plus backends/flock/cuda_live_patch.py and backends/flock/live (from --source).
# The verifier is `flock-live serve-gpu`, a separate process per shape on loopback (the prover never sees its RNG).
# env: ROUNDS=2 GPU_RUNS=3 SM=90 BUILD_ONLY
set -uxo pipefail
SM=${SM:-90}; SRC=$(pwd)
W=/workspace/flock-bench; F=$W/flock; O=$RESEARCH_RUN_DIR/out; mkdir -p $W $O
I=$RESEARCH_RUN_DIR/inputs
nvidia-smi; nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null; free -g
C13=/usr/local/cuda-13.3
if [ ! -x $C13/bin/nvcc ]; then
  export DEBIAN_FRONTEND=noninteractive
  . /etc/os-release; REPO=ubuntu${VERSION_ID/./}
  dpkg -s cuda-keyring >/dev/null 2>&1 || { wget -q https://developer.download.nvidia.com/compute/cuda/repos/$REPO/x86_64/cuda-keyring_1.1-1_all.deb && dpkg -i cuda-keyring_1.1-1_all.deb; }
  apt-get update -qq
  apt-get install -y -qq --no-install-recommends cuda-toolkit-13-3 >/dev/null || exit 1
fi
[ -x /usr/bin/time ] || apt-get install -y -qq time
DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | cut -d. -f1)
[ "$DRV" -lt 580 ] && { DEBIAN_FRONTEND=noninteractive apt-get install -y -qq cuda-compat-13-3 || exit 1; }
export PATH=$C13/bin:$PATH NVCC=$C13/bin/nvcc LD_LIBRARY_PATH=$C13/compat:$C13/lib64:${LD_LIBRARY_PATH:-}
command -v cargo >/dev/null || [ -x $HOME/.cargo/bin/cargo ] || curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/dev/null
source $HOME/.cargo/env; rustc --version
cd $W; [ -d flock ] || git clone -q https://github.com/succinctlabs/flock
cd $F && git checkout -q b684b12 && git checkout -q . && git log --oneline -1
sed -i "s/arch=compute_120,code=sm_120/arch=compute_$SM,code=sm_$SM/; s#/usr/local/cuda/lib64#$C13/lib64#g" crates/flock-cuda-ffi/build.rs
rm -rf crates/flock-live && cp -r $SRC/backends/flock/live crates/flock-live
grep -q '"crates/flock-live"' Cargo.toml || sed -i 's|    "crates/flock-transcript",|    "crates/flock-transcript",\n    "crates/flock-live",|' Cargo.toml
python3 $I/g128_patch.py || exit 1
python3 $SRC/backends/flock/cuda_live_patch.py || exit 1
mkdir -p $RESEARCH_RUN_DIR/fb/inputs
for f in $I/fb_*; do cp $f $RESEARCH_RUN_DIR/fb/inputs/$(basename $f | sed 's/^fb_//'); done
RESEARCH_RUN_DIR=$RESEARCH_RUN_DIR/fb BUILD_ONLY=1 bash $RESEARCH_RUN_DIR/fb/inputs/22-gpu-unit.sh || exit 1
NETS=$(ls -td $W/out/gpuunit-* | head -1)
cargo build --release -p flock-live --features verity-unit > $O/build-live.txt 2>&1 || { tail -40 $O/build-live.txt; exit 1; }
cargo test -p flock-cuda-ffi --release --features gpu --test gpu_roundtrip --no-run > $O/build-roundtrip.txt 2>&1 || { tail -40 $O/build-roundtrip.txt; exit 1; }
(git diff -- crates/flock-cuda-ffi cuda-ghash Cargo.toml; git status --short) > $O/flock-cuda-live.diff
nvidia-smi --query-gpu=name,driver_version,memory.total,clocks.max.sm --format=csv | tee $O/gpu.txt
[ "${BUILD_ONLY:-0}" = 1 ] && exit 0
LV=$F/target/release/flock-live
declare -A PORT
srv() {  # name table nbl [netlist]
  local key=$1 table=$2 nbl=$3 net=${4:-}; local port=$((7000 + ${#PORT[@]}))
  PORT[$key]=$port
  nice -n 5 $LV serve-gpu --listen 127.0.0.1:$port --out $O/sessions/$key --table $table --nbl $nbl ${net:+--netlist $net} > $O/serve-$key.log 2>&1 &
}
srv b19 blake3 19; srv b18 blake3 18; srv b17 blake3 17
srv u19 hopper_bf16 19 $NETS/net-hopper_bf16.txt; srv u17 hopper_bf16 17 $NETS/net-hopper_bf16.txt
srv e18 hopper_e4m3 18 $NETS/net-hopper_e4m3.txt
sleep 5; grep -h SERVING $O/serve-*.log
t() {  # key test-binary tag pipe(or -) nbl [env...]
  local key=$1 bin=$2 tag=$3 pipe=$4; shift 4
  local extra=(); [ "$pipe" != - ] && extra=(VU_NETLIST=$NETS/net-$pipe.txt VU_NAME=$pipe)
  local f=$O/$tag-${pipe}-${GPU_PROFILE}x${GPU_REPS}-live${GPU_LIVE}-${RTAG}.txt
  env "${extra[@]}" "$@" LIVE_VERIFIER=127.0.0.1:${PORT[$key]} GPU_PROFILE=$GPU_PROFILE GPU_REPS=$GPU_REPS GPU_LIVE=$GPU_LIVE /usr/bin/time -v \
    cargo test -p flock-cuda-ffi --release --features gpu --test $bin -- --ignored --nocapture --exact $tag > $f 2>&1
  echo "rc=$? $tag $pipe $GPU_PROFILE x$GPU_REPS live=$GPU_LIVE $RTAG"; grep -hE "G128RESULT|G128NEG|panicked|refused" $f | cut -c1-600
}
# live negatives first (each is a separate live session that must be rejected), then the witness tamper
export GPU_PROFILE=fast100 GPU_REPS=2 GPU_LIVE=1 RTAG=neg
t b17 gpu_roundtrip gpu_roundtrip_vs17 - GPU_RUNS=1 GPU_NEG=1
t u17 gpu_unit gpu_unit_nbl17 hopper_bf16 GPU_RUNS=1 GPU_NEG=1
RTAG=negw t u17 gpu_unit gpu_unit_nbl17 hopper_bf16 GPU_RUNS=1 VU_TAMPER_W=1 EXPECT_REJECT=1
for r in $(seq 1 ${ROUNDS:-2}); do
  for mode in "fast100 2 1" "fast100 2 0" "fast 1 0"; do
    read GPU_PROFILE GPU_REPS GPU_LIVE <<< "$mode"; export GPU_PROFILE GPU_REPS GPU_LIVE RTAG=r$r GPU_RUNS=${GPU_RUNS:-3}
    t b19 gpu_roundtrip gpu_roundtrip_vs19 -
    t b18 gpu_roundtrip gpu_roundtrip_vs18 -
    t u19 gpu_unit gpu_unit_nbl19 hopper_bf16
    t e18 gpu_unit gpu_unit_nbl18 hopper_e4m3
  done
done
kill $(jobs -p) 2>/dev/null
grep -h G128RESULT $O/*.txt | sed 's/^G128RESULT\t\?//; s/^G128RESULT //' > $O/results.jsonl
grep -h G128LIVE $O/*.txt > $O/live-sessions.txt
grep -h G128NEG $O/*.txt > $O/negatives.txt
cat $O/sessions/*/index.jsonl > $O/session-index.jsonl 2>/dev/null
true
