#!/usr/bin/env bash
# agkr-bound: the Rust verifier with link.rs (cargo build + test), then 31_link_rust.py on the R+leaf statement export 09
# left (cwd backends/gkr); [REL=bf16-ampere LEAF=sha256 REPS=3 BUILD_ONLY=].
# research run ... --send 31_link_rust.sh --send 31_link_rust.py -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/31_link_rust.sh"'
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT/tools/research/src:$ROOT:$HERE"
export PATH="/workspace/venv312/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
export CARGO_TARGET_DIR=/workspace/cargo-target
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT CARGO_BUILD_JOBS=$NT
echo "commit ${RESEARCH_SOURCE_COMMIT:-?}; threads $NT; MALLOC_MMAP_MAX_=$MALLOC_MMAP_MAX_ MALLOC_TRIM_THRESHOLD_=$MALLOC_TRIM_THRESHOLD_ ($(date -u +%H:%M:%S))"
echo "== 0. verifier ($(date -u +%H:%M:%S))"
( cd verifier && cargo build --release 2>&1 | grep -E "^(warning|error)|-->|^[0-9 ]+\||Finished" | head -60 ) 
[ -x $CARGO_TARGET_DIR/release/verity-gkr-verify ] || { echo "no verifier binary"; exit 2; }
( cd verifier && cargo test --release 2>&1 | grep -E "^test |^test result|FAILED|panicked|^error" | grep -vE "\.\.\. ok$" | head -40 )
( cd verifier && cargo test --release link 2>&1 | grep -E "^test " )
VB=/workspace/bin/verity-gkr-verify-link; mkdir -p /workspace/bin
cp $CARGO_TARGET_DIR/release/verity-gkr-verify $VB && sha256sum $VB
[ -n "${BUILD_ONLY:-}" ] && exit 0
export REL=${REL:-bf16-ampere} LEAF=${LEAF:-sha256}
O=/workspace/agkr-bound/link-rust-$REL; rm -rf $O
echo "== 1. link build + Rust ($(date -u +%H:%M:%S))"
/workspace/venv312/bin/python "$RESEARCH_RUN_DIR/inputs/31_link_rust.py" /workspace/agkr-bound/commit/$REL-$LEAF/stmt $O 4096 $NT ${REPS:-3} $VB
rc=$?
echo "rc=$rc ($(date -u +%H:%M:%S))"
exit $rc
