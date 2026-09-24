#!/usr/bin/env bash
# merge-postwave (CPU pod): toolchains for validate.sh, run while `research pods sync` ships the tree (~100 KB/s ingress):
# apt deps, rustup stable, sp1up v6.4.0 (succinct guest toolchain), uv + Python 3.12.  Idempotent.
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
stage "machine"; nproc; free -g | head -2; df -h /workspace | tail -1
stage "apt"
apt-get update -qq && apt-get install -y -qq --no-install-recommends \
  build-essential pkg-config libssl-dev clang libclang-dev cmake protobuf-compiler libprotobuf-dev \
  git jq golang-go time rsync >/dev/null; echo "apt rc=$?"
stage "rustup stable"
command -v rustup >/dev/null || curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/dev/null
rustup toolchain install stable --profile minimal >/dev/null; rustc --version
stage "sp1up v6.4.0"
if ! cargo prove --version 2>/dev/null | grep -q "6.4.0\|f66b4bf"; then
  curl -fsSL https://sp1up.succinct.xyz | bash >/dev/null
  "$HOME/.sp1/bin/sp1up" --version v6.4.0 2>&1 | tail -5
fi
cargo prove --version; rustup toolchain list
stage "uv + python 3.12"
command -v uv >/dev/null || curl -fsSL https://astral.sh/uv/install.sh | sh >/dev/null
uv --version; uv python install 3.12 >/dev/null; uv python find 3.12
stage "done"
