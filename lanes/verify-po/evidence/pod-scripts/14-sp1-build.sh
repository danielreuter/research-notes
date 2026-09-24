#!/usr/bin/env bash
# verify-po: build both SP1 CPU verifier hosts for the sp1-128 handoff 20260924T2220Z, on my pod.
#  1. STOCK host: backends/sp1 of MY tree /workspace/src (main ab9573fd; == lane/sp1-128 d1111579's backends/sp1 minus sec128/),
#     sp1up v6.4.0, cargo build --release --locked -p veritor-zk-host --features relation-bare (fills ~/.cargo/registry with
#     sp1-primitives 6.6.0) -> /workspace/bin/veritor-zk-host-relation-bare-stock-cpu
#  2. SEC134 host: lane/sp1-128 @ d1111579's backends/sp1/sec128/build.sh with VERIFIER_ONLY=1 (git archive of backends/sp1 at
#     d1111579 in /workspace/sp1-d1111579): the one-line core_fri_config change (124 -> 175 queries) in a copied cargo home,
#     backends/sp1 otherwise unmodified -> /workspace/bin/veritor-zk-host-relation-bare-sec134-cpu
# The apt list leaves out curl / ca-certificates (kb/ops-tools.md: apt upgrading curl on the runpod CPU image fails, rc 100).
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
O=/workspace/verify-po/sp1; mkdir -p $O /workspace/bin
{
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
for i in $(seq 1 60); do rustup toolchain list | grep -q succinct && break; sleep 10; done
cargo prove --version; rustup toolchain list | grep succinct
echo "=== [$(date -u +%H:%M:%S)] stock host (my tree)"
( cd /workspace/src/backends/sp1 && CARGO_TARGET_DIR=/workspace/sp1-target-stock cargo build --release --locked -p veritor-zk-host \
    --features relation-bare 2>&1 | grep -v -E "^\s+(Compiling|Downloaded|Downloading) " | tail -8 )
install -m 0755 /workspace/sp1-target-stock/release/veritor-zk-host /workspace/bin/veritor-zk-host-relation-bare-stock-cpu
sha256sum /workspace/bin/veritor-zk-host-relation-bare-stock-cpu
SP1_PROVER=cpu RUST_LOG=error /workspace/bin/veritor-zk-host-relation-bare-stock-cpu info 2>/dev/null | grep '^{' | tail -1
echo "=== [$(date -u +%H:%M:%S)] sec134 host (d1111579 sec128/build.sh VERIFIER_ONLY=1)"
cd /workspace/sp1-d1111579/backends/sp1 && SEC128_ROOT=/workspace/sec128-verifier VERIFIER_ONLY=1 bash sec128/build.sh 2>&1 | tail -40
echo "build.sh rc=${PIPESTATUS[0]}"
cat /workspace/sec128-verifier/verifier-source.diff /workspace/sec128-verifier/harness-source.diff 2>/dev/null
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee $O/build.out
