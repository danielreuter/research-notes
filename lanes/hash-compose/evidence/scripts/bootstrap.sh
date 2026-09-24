#!/usr/bin/env bash
# Bootstrap vy-hash-compose (RTX 4090, runpod/pytorch 2.4 cu12.4 devel image): the hp2-host recipe.
#   /workspace/venv312 : Python 3.12 + torch 2.6.0+cu124 + numpy + cupy-cuda12x + blake3 + pytest
#   rustup stable; cargo build --release of backends/ligero-verify -> /workspace/bin/ligero-verify
#   /workspace/bench-instances/v1 (the frozen bf16-ampere set: built from the committed seeds, sha256-pinned by manifest.json)
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
export CARGO_TARGET_DIR=/workspace/cargo-target
export DEBIAN_FRONTEND=noninteractive
SRC=${SRC:-/workspace/src}
PY=/workspace/venv312/bin/python
mkdir -p /workspace/bin /workspace/bench-instances /workspace/instances-cache
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
fail=0
stage "machine"
nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader; nproc; free -g | head -2; df -h /workspace | tail -1
grep -m1 'model name' /proc/cpuinfo; cat /proc/loadavg
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
import torch, numpy, cupy, blake3
print("torch", torch.__version__, "numpy", numpy.__version__, "cupy", cupy.__version__)
print("cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0), torch.version.cuda)
x = torch.randn(1024, 1024, device="cuda"); print("matmul ok", float((x @ x).sum()) != 0)
PYEOF
[ $? -eq 0 ] || fail=1
stage "bench instances -> /workspace/bench-instances/v1"
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC"
BI=/workspace/bench-instances/v1
NP=$(nproc); [ "$NP" -gt 16 ] && NP=16
if [ ! -f "$BI/vu-k1536.x.u16" ]; then
  "$PY" -m verity_numerical.bench.instances build --out "$BI" --seeds "$SRC/fixtures/bench-instances/v1/seeds" --procs "$NP" 2>&1 | tail -3
fi
ls "$BI" | head -30
[ -f "$BI/vu-k1536.x.u16" ] || fail=1
"$PY" - <<'PYEOF'
from pathlib import Path
from verity_numerical.bench import instances
import json, hashlib
bi = Path("/workspace/bench-instances/v1"); fz = Path("/workspace/src/fixtures/bench-instances/v1")
mb, mf = json.loads((bi/"manifest.json").read_text()), json.loads((fz/"manifest.json").read_text())
print("frozen manifest sha256", instances.manifest_sha256(fz))
print("built  manifest sha256", instances.manifest_sha256(bi))
for k in ("vu-k1536.x.u16","vu-k1536.w.u16","vu-k1536.acc.u32"):
    print(k, hashlib.sha256((bi/k).read_bytes()).hexdigest()[:16])
PYEOF
stage "rust build (join)"
wait $RUST_PID || fail=1
cat /tmp/rust_build.log
[ -x /workspace/bin/ligero-verify ] || fail=1
sha256sum /workspace/bin/ligero-verify
stage "done"
if [ $fail -eq 0 ]; then echo BOOTSTRAP_OK; else echo BOOTSTRAP_FAILED; exit 1; fi
