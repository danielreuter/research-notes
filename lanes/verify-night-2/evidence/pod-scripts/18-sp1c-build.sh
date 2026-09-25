#!/usr/bin/env bash
# verify-night-2: build sp1-committed's frame-v3 verifier host on MY pod, CPU only, from source b54e42ed (git archive
# sp1c-b54e42ed.tar.gz of backends/sp1 + fixtures/sp1-committed + verity/commitments; the guest / common are unchanged
# since the run's source cafa9464, host-only diff = `committed-verify --batch`).
#   STAGE=toolchain | build | all  bash 18-sp1c-build.sh
# toolchain: apt, rustup stable, sp1up v6.4.0 (+ the succinct guest toolchain); build: cargo build --release --locked
# -p veritor-zk-host --features relation-committed (ELF from build.rs, path-remapped) -> /workspace/bin/veritor-zk-host-
# committed-b54e42ed-cpu; `info` (vk, ELF sha) and cargo test -p veritor-zk-common committed (core frame-v3 vectors).
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
I=$RESEARCH_RUN_DIR/inputs; STAGE=${STAGE:-all}; S=/workspace/sp1c-b54e42ed; O=/workspace/verify-night-2/sp1c; mkdir -p $O /workspace/bin
{
if [ $STAGE = toolchain ] || [ $STAGE = all ]; then
  echo "=== [$(date -u +%H:%M:%S)] apt"
  apt-get update -qq && apt-get install -y -qq --no-install-recommends build-essential pkg-config libssl-dev clang libclang-dev cmake \
    protobuf-compiler libprotobuf-dev git jq >/dev/null; echo "apt rc=$?"
  echo "=== [$(date -u +%H:%M:%S)] rustup + sp1up v6.4.0"
  command -v rustup >/dev/null || curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/dev/null
  rustup toolchain install stable --profile minimal >/dev/null
  if ! cargo prove --version 2>/dev/null | grep -q "6.4.0"; then
    curl -fsSL https://sp1up.succinct.xyz | bash >/dev/null
    "$HOME/.sp1/bin/sp1up" --version v6.4.0
  fi
  for i in $(seq 1 90); do rustup toolchain list | grep -q succinct && break; sleep 10; done
  cargo prove --version; rustup toolchain list | grep succinct
fi
if [ $STAGE = build ] || [ $STAGE = all ]; then
  echo "=== [$(date -u +%H:%M:%S)] source"
  rm -rf $S; mkdir -p $S; tar -xzf $I/sp1c-b54e42ed.tar.gz -C $S; sha256sum $I/sp1c-b54e42ed.tar.gz; ls $S $S/backends/sp1
  echo "=== [$(date -u +%H:%M:%S)] cargo build (relation-committed, CPU)"
  ( cd $S/backends/sp1 && CARGO_TARGET_DIR=/workspace/sp1c-target cargo build --release --locked -p veritor-zk-host \
      --features relation-committed 2>&1 | grep -v -E "^\s+(Compiling|Downloaded|Downloading) " | tail -8; echo "build rc=${PIPESTATUS[0]}" )
  install -m 0755 /workspace/sp1c-target/release/veritor-zk-host /workspace/bin/veritor-zk-host-committed-b54e42ed-cpu
  sha256sum /workspace/bin/veritor-zk-host-committed-b54e42ed-cpu
  SP1_PROVER=cpu RUST_LOG=error /workspace/bin/veritor-zk-host-committed-b54e42ed-cpu info 2>/dev/null | grep '^{' | tail -1 | tee $O/info.json
  echo "=== [$(date -u +%H:%M:%S)] cargo test -p veritor-zk-common committed"
  ( cd $S/backends/sp1 && CARGO_TARGET_DIR=/workspace/sp1c-target cargo test --release --locked -p veritor-zk-common --features relation-committed \
      committed 2>&1 | grep -E "^test |test result|error" | tail -30 )
fi
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee -a $O/build.out
