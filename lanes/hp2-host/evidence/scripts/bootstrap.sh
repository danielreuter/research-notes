#!/usr/bin/env bash
# Bootstrap vy-hp2-host (RTX 4090, runpod/pytorch 2.4 cu12.4 devel image) for lane hp2-host: the hostphase / b-merge-h100 recipe.
#   /workspace/venv312 : Python 3.12 + torch 2.6.0+cu124 + numpy + cupy-cuda12x + blake3 + pytest
#   rustup stable; cargo build --release of backends/ligero-verify -> /workspace/bin/ligero-verify
#   /workspace/bench-instances/v1 (the bf16-ampere gate reads it); relation instance caches (bf16-hopper, fp8-hopper, 4096 VUs)
#   /workspace/src-main : a copy of THIS shipped tree (= main 6babe27 at bootstrap time: the baseline / bit-exactness reference)
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
nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader; nproc; free -g | head -2; df -h /workspace | tail -1
grep -m1 'model name' /proc/cpuinfo; cat /proc/loadavg
echo "source tree: $SRC"; cat "$SRC/.research-source.json" 2>/dev/null || true

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

stage "torch 2.6.0+cu124, numpy, cupy-cuda12x, blake3, pytest"
if ! "$PY" -c "import torch; assert torch.__version__.startswith('2.6.0')" 2>/dev/null; then
  uv pip install --python "$PY" --index-url https://download.pytorch.org/whl/cu124 "torch==2.6.0" 2>&1 | tail -2
fi
uv pip install --python "$PY" numpy cupy-cuda12x blake3 pytest 2>&1 | tail -2
"$PY" - <<'PYEOF'
import torch, triton, numpy, cupy, blake3
print("torch", torch.__version__, "triton", triton.__version__, "numpy", numpy.__version__, "cupy", cupy.__version__)
print("cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0), torch.version.cuda)
x = torch.randn(1024, 1024, device="cuda"); print("matmul ok", float((x @ x).sum()) != 0)
y = cupy.arange(16, dtype=cupy.uint32); print("cupy ok", int(y.sum()) == 120)
import hashlib, time
t0=time.perf_counter(); raw=hashlib.shake_256(b"x"*32).digest(3<<20); dt=time.perf_counter()-t0
print(f"hashlib shake_256 squeeze 3 MiB: {dt*1e3:.2f} ms ({3*2**20/dt/1e6:.0f} MB/s)")
import _hashlib; print("openssl", getattr(_hashlib, "openssl_version_info", None))
PYEOF
[ $? -eq 0 ] || fail=1

stage "bench instances -> /workspace/bench-instances/v1 (background)"
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC"
BI=/workspace/bench-instances/v1
NP=$(nproc); [ "$NP" -gt 16 ] && NP=16
( if [ ! -f "$BI/vu-k1536.x.u16" ]; then
    "$PY" -m verity_numerical.bench.instances build --out "$BI" --seeds "$SRC/fixtures/bench-instances/v1/seeds" --procs "$NP" 2>&1 | tail -3
  fi; ls "$BI" | head -30; echo INST_OK ) > /tmp/inst_build.log 2>&1 &
INST_PID=$!

stage "relation instance caches (bf16-hopper, fp8-hopper, 4096 VUs)"
"$PY" - <<'PYEOF'
import time
from backends.direct.ligero.relchain import instances
from backends.direct.ligero.relations import relation
for name in ("bf16-hopper", "fp8-hopper"):
    t0 = time.perf_counter(); d = instances(relation(name), 4096, procs=16, cache="/workspace/instances-cache"); print(name, len(d), f"{time.perf_counter()-t0:.1f}s")
PYEOF
[ $? -eq 0 ] || fail=1
ls -la /workspace/instances-cache

stage "rust build (join)"
wait $RUST_PID || fail=1
cat /tmp/rust_build.log
[ -x /workspace/bin/ligero-verify ] || fail=1
sha256sum /workspace/bin/ligero-verify

stage "instances (join)"
wait $INST_PID || fail=1
cat /tmp/inst_build.log
[ -f "$BI/vu-k1536.x.u16" ] || fail=1

stage "versions"
uv pip list --python "$PY" | grep -Ei "^(torch|triton|numpy|cupy|blake3|pytest) "
"$HOME/.cargo/bin/rustc" --version
df -h /workspace | tail -1

stage "done"
if [ $fail -eq 0 ]; then echo BOOTSTRAP_OK; else echo BOOTSTRAP_FAILED; exit 1; fi
