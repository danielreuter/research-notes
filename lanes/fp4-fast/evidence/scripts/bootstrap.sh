#!/usr/bin/env bash
# Bootstrap vy-fp4-fast (RTX 5090, runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel image) for lane fp4-fast, fp4-proof's recipe:
#   /workspace/venv312 : Python 3.12 + torch 2.8.0+cu128 + numpy + cupy-cuda12x + blake3 + pytest
#   rustup stable; cargo build --release of backends/ligero-verify -> /workspace/bin/ligero-verify
#   /workspace/bench-instances/v1 (the bf16-ampere gate reads it)
#   /workspace/src-main : a copy of THIS shipped tree (main 6babe27: the baseline / bit-exactness reference)
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
export CARGO_TARGET_DIR=/workspace/cargo-target
export DEBIAN_FRONTEND=noninteractive
SRC=$(pwd)
PY=/workspace/venv312/bin/python
mkdir -p /workspace/bin /workspace/bench-instances /workspace/instances-cache
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
fail=0

stage "machine"
nvidia-smi --query-gpu=name,uuid,memory.total,driver_version,power.limit,clocks.max.sm --format=csv,noheader; nproc; free -g | head -2; df -h /workspace | tail -1
cat /sys/fs/cgroup/cpu.max 2>/dev/null || true; grep -m1 'model name' /proc/cpuinfo; cat /proc/loadavg
echo "source tree: $SRC"; cat "$SRC/.research-source.json" 2>/dev/null || true; which nvcc cuobjdump || true; nvcc --version | tail -1

stage "src-main copy (main 6babe27 reference)"
if [ ! -d /workspace/src-main ]; then cp -a "$SRC" /workspace/src-main; fi
ls /workspace/src-main | head -5

stage "rustup stable + ligero-verify (background)"
( if ! command -v cargo >/dev/null 2>&1; then curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/tmp/rustup.log 2>&1; fi
  "$HOME/.cargo/bin/rustc" --version
  cd "$SRC/backends/ligero-verify" && cargo build --release 2>&1 | tail -3 && cp "$CARGO_TARGET_DIR/release/ligero-verify" /workspace/bin/
  ls -la /workspace/bin; echo RUST_OK ) > /tmp/rust_build.log 2>&1 &
RUST_PID=$!

stage "uv + python 3.12 + venv312"
if ! command -v uv >/dev/null 2>&1; then curl -fsSL https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; fi
uv --version
uv python install 3.12 2>&1 | tail -1
if [ ! -x "$PY" ]; then uv venv /workspace/venv312 --python 3.12 2>&1 | tail -1; fi
"$PY" --version

stage "torch 2.8.0+cu128, numpy, cupy-cuda12x, blake3, pytest"
if ! "$PY" -c "import torch; assert torch.__version__.startswith('2.8.0')" 2>/dev/null; then
  uv pip install --python "$PY" --index-url https://download.pytorch.org/whl/cu128 "torch==2.8.0" 2>&1 | tail -2
fi
uv pip install --python "$PY" numpy cupy-cuda12x blake3 pytest 2>&1 | tail -2
"$PY" - <<'PYEOF'
import torch, numpy, cupy, blake3
print("torch", torch.__version__, "numpy", numpy.__version__, "cupy", cupy.__version__)
print("cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0), torch.version.cuda, torch.cuda.get_device_capability(0))
x = torch.randn(1024, 1024, device="cuda"); print("matmul ok", float((x @ x).sum()) != 0)
y = cupy.arange(16, dtype=cupy.uint32); print("cupy ok", int(y.sum()) == 120)
k = cupy.RawKernel(r'extern "C" __global__ void f(unsigned* x){ x[threadIdx.x] += 1; }', "f"); z = cupy.zeros(8, dtype=cupy.uint32); k((1,),(8,),(z,)); print("nvrtc ok", int(z.sum()) == 8)
PYEOF
[ $? -eq 0 ] || fail=1

stage "bench instances -> /workspace/bench-instances/v1 (background)"
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC"
BI=/workspace/bench-instances/v1
NP=$(nproc); [ "$NP" -gt 12 ] && NP=12
( if [ ! -f "$BI/vu-k1536.x.u16" ]; then
    "$PY" -m verity_numerical.bench.instances build --out "$BI" --seeds "$SRC/fixtures/bench-instances/v1/seeds" --procs "$NP" 2>&1 | tail -5
  fi; ls "$BI" | head -30; echo INST_OK ) > /tmp/inst_build.log 2>&1 &
INST_PID=$!

stage "fp4 smoke: compile the relation, numpy hints on 1024 units"
"$PY" - <<'PYEOF'
import time, numpy as np
from backends.direct.ligero.fp4.relation import compile_fp4_unit
from backends.direct.ligero.fp4.witness import random_units, hints_fp4, oracle_words, unit_hints
t0 = time.perf_counter(); s = compile_fp4_unit(); print("compiled", s.summary(), f"{time.perf_counter()-t0:.2f}s")
rng = np.random.default_rng(1); c, a, b = random_units(rng, 4096, "random")
t0 = time.perf_counter(); H = hints_fp4(s, c, a, b); print("numpy hints (4096 units):", H.shape, f"{time.perf_counter()-t0:.3f}s")
_, y = unit_hints(c, a, b); print("hint words == oracle:", bool((y == oracle_words(c[:256], a[:256], b[:256])[:256]).all()) if False else bool((y[:256] == oracle_words(c[:256], a[:256], b[:256])).all()))
PYEOF
[ $? -eq 0 ] || fail=1

stage "rust build (join)"
wait $RUST_PID || fail=1
cat /tmp/rust_build.log
[ -x /workspace/bin/ligero-verify ] || fail=1
/workspace/bin/ligero-verify 2>&1 | head -1
sha256sum /workspace/bin/ligero-verify

stage "instances (join)"
wait $INST_PID || fail=1
cat /tmp/inst_build.log
[ -f "$BI/vu-k1536.x.u16" ] || fail=1

stage "versions"
uv pip list --python "$PY" | grep -Ei "^(torch|numpy|cupy|blake3|pytest) "
"$HOME/.cargo/bin/rustc" --version
df -h /workspace | tail -1

stage "done"
if [ $fail -eq 0 ]; then echo BOOTSTRAP_OK; else echo BOOTSTRAP_FAILED; exit 1; fi
