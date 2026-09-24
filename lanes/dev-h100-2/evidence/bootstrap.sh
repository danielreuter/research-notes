#!/usr/bin/env bash
# Bootstrap vy-dev-h100-2 (runpod/pytorch 2.4 cu12.4 devel image) for lane dev-h100-2 = dev-a100's recipe on the post-freeze tree 11c7075:
#   /workspace/venv312 : Python 3.12 + torch 2.6.0+cu124 + numpy + cupy-cuda12x + blake3 + pytest + pytest-timeout
#   rustup stable; cargo build --release of backends/ligero-verify -> /workspace/bin/ligero-verify
#   synthetic instance caches for bf16-hopper / fp8-hopper (n = 2048 gate, 4096 bench) under /workspace/instances-cache
# SRC = /workspace/src -> /workspace/research/src/<sha of 11c7075> (frozen 64c00bd GitHub tarball + git diff 64c00bd..11c7075, blob-sha verified).
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
export CARGO_TARGET_DIR=/workspace/cargo-target
export DEBIAN_FRONTEND=noninteractive
SRC=/workspace/src
PY=/workspace/venv312/bin/python
mkdir -p /workspace/bin /workspace/instances-cache /workspace/research
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
fail=0

stage "machine"
nvidia-smi --query-gpu=name,uuid,memory.total,driver_version,power.limit,clocks.max.sm --format=csv,noheader; nproc; free -g | head -2; df -h /workspace | tail -1
cat /sys/fs/cgroup/cpu.max 2>/dev/null || true; grep -m1 'model name' /proc/cpuinfo; cat /proc/loadavg; hostname
tr "\0" "\n" < /proc/1/environ | grep -E "RUNPOD_(DC_ID|PUBLIC_IP|POD_ID)" || true
echo "source tree: $SRC -> $(readlink -f $SRC)"; ls "$SRC" | head -5

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

stage "torch 2.6.0+cu124, numpy, cupy-cuda12x, blake3, pytest, pytest-timeout"
if ! "$PY" -c "import torch; assert torch.__version__.startswith('2.6.0')" 2>/dev/null; then
  uv pip install --python "$PY" --index-url https://download.pytorch.org/whl/cu124 "torch==2.6.0" 2>&1 | tail -2
fi
uv pip install --python "$PY" numpy cupy-cuda12x blake3 pytest pytest-timeout 2>&1 | tail -2
"$PY" - <<'PYEOF'
import torch, numpy, blake3, cupy
print("torch", torch.__version__, "numpy", numpy.__version__, "cupy", cupy.__version__)
print("cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0), torch.version.cuda, torch.cuda.get_device_capability(0))
print("device memory bytes", torch.cuda.get_device_properties(0).total_memory)
x = torch.randn(1024, 1024, device="cuda"); print("matmul ok", float((x @ x).sum()) != 0)
y = cupy.arange(16, dtype=cupy.uint32); print("cupy ok", int(y.sum()) == 120)
PYEOF
[ $? -eq 0 ] || fail=1
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
cd "$SRC" && "$PY" - <<'PYEOF'
from backends.direct.ligero import merkle
print("merkle.gpu_available():", merkle.gpu_available(), "|", merkle.HASH_NAME, "|", getattr(merkle, "GPU_HASH_NAME", None))
assert merkle.gpu_available(), "GPU Merkle path unavailable: the prover would fall back to host hashing"
PYEOF
[ $? -eq 0 ] || fail=1

stage "instance caches (bf16-hopper, fp8-hopper; n = 2048 and 4096) -> /workspace/instances-cache"
cd "$SRC" && OMP_NUM_THREADS=1 "$PY" - <<'PYEOF'
import time, hashlib
from backends.direct.ligero import relchain
from backends.direct.ligero.relations import relation
from verity_numerical.bench import contract
for name, want in (("bf16-hopper", contract.BF16_HOPPER_INSTANCES_DIGEST), ("fp8-hopper", contract.FP8_HOPPER_INSTANCES_DIGEST)):
    rel = relation(name)
    for n in (2048, 4096):
        t0 = time.perf_counter()
        d = relchain.instances(rel, n, procs=16, cache="/workspace/instances-cache")
        print(f"{name} n={n}: {len(d)} VUs in {time.perf_counter()-t0:.1f}s; digest {relchain.instances_digest(rel, n)[:16]}...")
    dg = relchain.instances_digest(rel, 4096)
    print(f"{name} instances_digest(4096) = {dg}  frozen? {dg == want}")
    assert dg == want, f"{name}: digest {dg} != frozen {want}"
PYEOF
[ $? -eq 0 ] || fail=1
ls -la /workspace/instances-cache

stage "rust build (join)"
wait $RUST_PID || fail=1
cat /tmp/rust_build.log
[ -x /workspace/bin/ligero-verify ] || fail=1
/workspace/bin/ligero-verify --help 2>&1 | head -2
sha256sum /workspace/bin/ligero-verify

stage "versions"
uv pip list --python "$PY" | grep -Ei "^(torch|triton|numpy|blake3|pytest|pytest-timeout|cupy) "
"$HOME/.cargo/bin/rustc" --version
df -h /workspace | tail -1

stage "done"
if [ $fail -eq 0 ]; then echo BOOTSTRAP_OK; else echo BOOTSTRAP_FAILED; exit 1; fi
