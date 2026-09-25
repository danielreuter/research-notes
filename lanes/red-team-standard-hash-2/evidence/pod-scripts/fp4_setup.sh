#!/usr/bin/env bash
# red-team-standard-hash-2, 18:07Z: CPU pod setup for the fp4-nvf4+poseidon2 class review (tree /workspace/src = main
# cd963fd4 + the rtsh overlay, via `research pods sync`): python 3.12 venv with torch (CPU) + numpy + blake3, rust, and
# ligero-verify built from that tree.
set -euo pipefail
cd /workspace
pip3 -q install uv
[ -x venv312/bin/python ] || uv venv -q -p 3.12 venv312
VIRTUAL_ENV=/workspace/venv312 uv pip install -q --index-url https://download.pytorch.org/whl/cpu torch
VIRTUAL_ENV=/workspace/venv312 uv pip install -q numpy blake3 pytest
command -v cargo >/dev/null || (curl -sSf https://sh.rustup.rs | sh -s -- -y -q --profile minimal)
export PATH="$HOME/.cargo/bin:$PATH"
cd /workspace/src
CARGO_TARGET_DIR=/workspace/cargo-target cargo build -q --release --manifest-path backends/ligero-verify/Cargo.toml
mkdir -p /workspace/bin && cp /workspace/cargo-target/release/ligero-verify /workspace/bin/ligero-verify
sha256sum /workspace/bin/ligero-verify
/workspace/venv312/bin/python -c "import sys, torch, numpy; print(sys.version.split()[0], torch.__version__, numpy.__version__)"
