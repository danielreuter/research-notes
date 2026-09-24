#!/usr/bin/env bash
# Bootstrap vy-dev-4090 (RTX 4090 24 GiB reference part, EU-RO-1) for lane dev-4090: the merge-val / hash-relation recipe.
#   /workspace/venv312 : Python 3.12 + torch 2.6.0+cu124 + numpy + cupy-cuda12x + blake3 + pytest
#   rustup stable; cargo build --release of backends/ligero-verify (in-tree target dir) -> /workspace/bin/ligero-verify
#   fp8-ada + fp8-ada-v2 instance caches (4096 VUs) in /workspace/instances-cache
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
export DEBIAN_FRONTEND=noninteractive
SRC=/workspace/src
PY=/workspace/venv312/bin/python
mkdir -p /workspace/bin /workspace/instances-cache /workspace/prace
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
fail=0

stage "machine"
nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader; nproc; free -g | head -2; df -h /workspace | tail -1
grep -m1 'model name' /proc/cpuinfo; cat /proc/loadavg; hostname
cat /proc/1/environ | tr '\0' '\n' | grep -i RUNPOD_DC || true
cd "$SRC" && cat COMMIT 2>/dev/null || true

stage "rustup stable + ligero-verify (background)"
( if ! command -v cargo >/dev/null 2>&1; then curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/tmp/rustup.log 2>&1; fi
  "$HOME/.cargo/bin/rustc" --version
  cd "$SRC/backends/ligero-verify" && cargo build --release 2>&1 | tail -3 && cp target/release/ligero-verify /workspace/bin/
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
import torch, numpy, cupy, blake3
print("torch", torch.__version__, "numpy", numpy.__version__, "cupy", cupy.__version__)
print("cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0), torch.version.cuda)
print("total_memory", torch.cuda.get_device_properties(0).total_memory)
x = torch.randn(1024, 1024, device="cuda"); print("matmul ok", float((x @ x).sum()) != 0)
PYEOF
[ $? -eq 0 ] || fail=1

stage "import smoke (frozen tree)"
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
cd "$SRC" && "$PY" -c "import backends.direct.ligero.run, backends.direct.ligero.pipeline, backends.direct.ligero.witness_device, backends.direct.ligero.live; print('imports ok')"
[ $? -eq 0 ] || fail=1

stage "instance caches (fp8-ada, fp8-ada-v2: 4096 VUs)"
"$PY" - <<'PYEOF'
import time
from backends.direct.ligero.relchain import instances
from backends.direct.ligero.relations import relation
for name in ("fp8-ada",):
    t0 = time.perf_counter(); d = instances(relation(name), 4096, procs=16, cache="/workspace/instances-cache"); print(name, len(d), f"{time.perf_counter()-t0:.1f}s", flush=True)
PYEOF
[ $? -eq 0 ] || fail=1
ls -la /workspace/instances-cache

stage "live probe (skipped)"

stage "rust build (join)"
wait $RUST_PID || fail=1
cat /tmp/rust_build.log
[ -x /workspace/bin/ligero-verify ] || fail=1
sha256sum /workspace/bin/ligero-verify

stage "versions"
uv pip list --python "$PY" | grep -Ei "^(torch|numpy|cupy|blake3|pytest) "
"$HOME/.cargo/bin/rustc" --version
df -h /workspace | tail -1

stage "done"
if [ $fail -eq 0 ]; then echo BOOTSTRAP_OK; else echo BOOTSTRAP_FAILED; exit 1; fi
