#!/usr/bin/env bash
# verify-po: the sec134 CPU verifier host, second try. d1111579's sec128/build.sh VERIFIER_ONLY=1 still patches sp1-cuda 6.4.0's
# client.rs in the copied cargo home, which a CPU-only (relation-bare) stock build never downloads ("sp1-cuda retry loop not found
# once", rc 2). `cargo fetch --locked` in backends/sp1 downloads every locked crate (sp1-cuda included) without building it; the
# build script then runs unmodified. The harness patch touches only sp1-cuda, which the relation-bare host does not compile.
set -uo pipefail
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
O=/workspace/verify-po/sp1
{
echo "=== [$(date -u +%H:%M:%S)] cargo fetch --locked (my tree's backends/sp1, same Cargo.lock as d1111579)"
cmp /workspace/src/backends/sp1/Cargo.lock /workspace/sp1-d1111579/backends/sp1/Cargo.lock && echo "Cargo.lock identical"
(cd /workspace/src/backends/sp1 && cargo fetch --locked 2>&1 | tail -2)
ls -d $HOME/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/sp1-cuda-6.4.0
echo "=== [$(date -u +%H:%M:%S)] sec134 host (d1111579 sec128/build.sh VERIFIER_ONLY=1)"
cd /workspace/sp1-d1111579/backends/sp1 && SEC128_ROOT=/workspace/sec128-verifier VERIFIER_ONLY=1 bash sec128/build.sh 2>&1 | grep -v "^\s*$" | tail -30
echo "build.sh rc=${PIPESTATUS[0]}"
sha256sum /workspace/bin/veritor-zk-host-relation-bare-sec134-cpu
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee $O/build-sec134.out
