#!/usr/bin/env bash
# ligero-steps-pin: CPU pod setup (pod_bootstrap.sh assumes a GPU).  rustup stable + ligero-verify release build,
# uv Python 3.12 venv with CPU torch, numpy, blake3, pytest.  Idempotent.  Leaves /workspace/env.sh.
set -uo pipefail
SRC=${SRC:-/workspace/src}
W=/workspace
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
export CARGO_TARGET_DIR=$W/cargo-target
mkdir -p $W/bin
command -v rsync >/dev/null || { apt-get update -qq && apt-get install -y -qq --no-install-recommends rsync build-essential >/dev/null; }
command -v cc >/dev/null || { apt-get update -qq && apt-get install -y -qq --no-install-recommends build-essential >/dev/null; }
command -v cargo >/dev/null || curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/tmp/rustup.log 2>&1
rustup update stable >/dev/null 2>&1 || true
rustc --version; cargo --version
command -v uv >/dev/null || curl -fsSL https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
uv python install 3.12 2>&1 | tail -1
[ -x $W/venv312/bin/python ] || uv venv $W/venv312 --python 3.12 2>&1 | tail -1
PY=$W/venv312/bin/python
$PY -c "import torch" 2>/dev/null || uv pip install --python $PY --index-url https://download.pytorch.org/whl/cpu "torch==2.6.0" 2>&1 | tail -1
uv pip install --python $PY numpy blake3 pytest pytest-timeout 2>&1 | tail -1
cat > $W/env.sh <<EOF
export PY=$PY
export PATH="$W/venv312/bin:\$HOME/.cargo/bin:\$HOME/.local/bin:\$PATH"
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
export CARGO_TARGET_DIR=$CARGO_TARGET_DIR
export LIGERO_VERIFY=$W/bin/ligero-verify
export OMP_NUM_THREADS=\$(nproc)
EOF
$PY -c "import torch, numpy, blake3; print('torch', torch.__version__)"
