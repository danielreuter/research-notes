#!/usr/bin/env bash
# verify-night-3: CPU pod setup for SP1 verification (no proving): python 3.12 venv, rust, sp1up v6.4.0, and the CPU
# veritor-zk-host built from this tree's backends/sp1 (its build compiles the guest ELF; `info` must print the APPROVED
# identity). Writes /workspace/env.sh (PY, PATH) for lib.sh.
set -uo pipefail
SRC=$(pwd); W=/workspace
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq --no-install-recommends clang libclang-dev cmake protobuf-compiler pkg-config libssl-dev git curl build-essential >/dev/null
command -v uv >/dev/null 2>&1 || curl -fsSL https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.sp1/bin:$PATH"
uv python install 3.12 >/dev/null 2>&1; [ -x $W/venv312/bin/python ] || uv venv $W/venv312 --python 3.12 >/dev/null
uv pip install -q --python $W/venv312/bin/python numpy
command -v cargo >/dev/null || curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/dev/null 2>&1
command -v sp1up >/dev/null || curl -fsSL https://sp1up.succinct.xyz | bash >/dev/null 2>&1
sp1up --version v6.4.0 2>&1 | tail -2
cat > $W/env.sh <<EOF
export PY=$W/venv312/bin/python
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.sp1/bin:\$PATH"
EOF
source $W/env.sh
cd $SRC/backends/sp1 && time cargo build --release -p veritor-zk-host 2>&1 | tail -3
mkdir -p $W/bin && cp target/release/veritor-zk-host $W/bin/veritor-zk-host-cpu && sha256sum $W/bin/veritor-zk-host-cpu
$W/bin/veritor-zk-host-cpu info | tail -1
