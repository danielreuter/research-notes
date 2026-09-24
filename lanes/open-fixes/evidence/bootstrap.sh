#!/usr/bin/env bash
# Bootstrap a lane open-fixes pod (RTX 4090 or H100): the blake3-leaf / dev-h100-2 recipe.
#   /workspace/venv312 : Python 3.12 + torch 2.6.0+cu124 + numpy + cupy-cuda12x + blake3 + pytest + pytest-timeout
#   rustup stable; cargo build --release of backends/ligero-verify -> /workspace/bin/ligero-verify
#   instance caches under /workspace/instances-cache for the relations named in $RELS (default fp8-ada)
# SRC = /workspace/src (the lane tree shipped with `git archive HEAD | ssh tar -x`).
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
export CARGO_TARGET_DIR=/workspace/cargo-target
export DEBIAN_FRONTEND=noninteractive
SRC=${SRC:-/workspace/src}
RELS=${RELS:-fp8-ada}
PY=/workspace/venv312/bin/python
mkdir -p /workspace/bin /workspace/instances-cache
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
fail=0

stage "machine"
nvidia-smi --query-gpu=name,uuid,memory.total,driver_version,power.limit,clocks.max.sm --format=csv,noheader; nproc; free -g | head -2; df -h /workspace | tail -1
cat /sys/fs/cgroup/cpu.max 2>/dev/null || true; grep -m1 'model name' /proc/cpuinfo; cat /proc/loadavg; hostname
echo "source tree: $SRC"; cat "$SRC/TREE_SHA" 2>/dev/null || true

stage "rustup stable + ligero-verify (background)"
( if ! command -v cargo >/dev/null 2>&1; then curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/tmp/rustup.log 2>&1; fi
  "$HOME/.cargo/bin/rustc" --version
  cd "$SRC/backends/ligero-verify" && cargo build --release 2>&1 | tail -3 && cp "$CARGO_TARGET_DIR/release/ligero-verify" /workspace/bin/
  ls -la /workspace/bin; echo RUST_OK ) > /tmp/rust_build.log 2>&1 &
RUST_PID=$!

stage "uv + python 3.12 + venv312"
if ! command -v uv >/dev/null 2>&1; then curl -fsSL https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; fi
export PATH="$HOME/.local/bin:$PATH"
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
x = torch.randn(1024, 1024, device="cuda"); print("matmul ok", float((x @ x).sum()) != 0)
y = cupy.arange(16, dtype=cupy.uint32); print("cupy ok", int(y.sum()) == 120)
PYEOF
[ $? -eq 0 ] || fail=1
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
cd "$SRC" && "$PY" - <<'PYEOF'
from backends.direct.ligero import merkle
print("merkle.gpu_available():", merkle.gpu_available(), "|", merkle.HASH_NAME, "|", getattr(merkle, "GPU_HASH_NAME", None))
assert merkle.gpu_available(), "GPU Merkle path unavailable"
PYEOF
[ $? -eq 0 ] || fail=1

stage "instance caches ($RELS; n = 2048, 4096)"
cd "$SRC" && RELS="$RELS" OMP_NUM_THREADS=1 "$PY" - <<'PYEOF'
import os, time
from backends.direct.ligero import relchain
from backends.direct.ligero.relations import relation
for name in os.environ["RELS"].split(","):
    rel = relation(name)
    for n in (2048, 4096):
        t0 = time.perf_counter()
        d = relchain.instances(rel, n, procs=8, cache="/workspace/instances-cache")
        print(f"{name} n={n}: {len(d)} VUs in {time.perf_counter()-t0:.1f}s; digest {relchain.instances_digest(rel, n)[:16]}...", flush=True)
PYEOF
[ $? -eq 0 ] || fail=1

stage "rust build (join)"
wait $RUST_PID || fail=1
cat /tmp/rust_build.log
[ -x /workspace/bin/ligero-verify ] || fail=1
sha256sum /workspace/bin/ligero-verify

stage "versions"
uv pip list --python "$PY" | grep -Ei "^(torch|triton|numpy|blake3|pytest|pytest-timeout|cupy) "
"$HOME/.cargo/bin/rustc" --version
df -h /workspace | tail -1

stage "done"
if [ $fail -eq 0 ]; then echo BOOTSTRAP_OK; else echo BOOTSTRAP_FAILED; exit 1; fi
