#!/usr/bin/env bash
# TC_DOT_BF16 on the pod: fork worktree at 3510b39a7 + the BF16 patch, unit + chip tests, cost-artifact regeneration,
# then the BF16-capable sp1-gpu-server installed under $W/bf16-root (the fp8 server in ~/.sp1/bin stays for the op-bench).
set -euo pipefail
W=/workspace/sp1-tcdot
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:/usr/local/go/bin:$PATH"
export CUDACXX=/usr/local/cuda/bin/nvcc CUDA_ARCHS=80
export CARGO_TARGET_DIR=$W/target-bf16
stamp() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }

stamp "worktree + patch"
cd "$W/sp1"
[ -d "$W/sp1-bf16" ] || git worktree add -f --detach "$W/sp1-bf16" 3510b39a71afd587c8076fd3ddd18a1ccbd23818
cd "$W/sp1-bf16"
git reset -q --hard 3510b39a71afd587c8076fd3ddd18a1ccbd23818
git -c user.name="verity sp1-tcdot lane" -c user.email="lane@verity.local" am -q "$W"/patches/*.patch
git log --oneline -2
git rev-parse HEAD > "$W/bf16-fork-head"

filter() { grep -E "^test |test result|^error|^warning: unused|panicked|FAILED|failures:" || true; }

stamp "executor unit tests (tc_dot)"
cargo test --release -p sp1-core-executor --lib tc_dot 2>&1 | filter

stamp "regenerate cost/complexity artifacts"
(cd crates/core/machine && cargo test --release -p sp1-core-machine --lib -- --ignored --exact \
   riscv::tests::write_core_air_costs riscv::tests::write_core_air_complexity 2>&1 | filter)
python3 - <<'EOF'
import json
for f in ["rv64im_costs.json", "rv64im_complexity.json"]:
    d = json.load(open(f"crates/core/executor/src/artifacts/{f}"))
    print(f, {k: d[k] for k in ["TcDot", "TcDotUser", "TcDotBf16", "TcDotBf16User"]})
EOF
git diff --stat

stamp "chip tests (fp8 + bf16, incl. consistency)"
cargo test --release -p sp1-core-machine --lib -- tc_dot core_air_cost_consistency core_air_complexity_consistency \
   test_maximum_cycle test_maximum_padding 2>&1 | filter

stamp "BF16 sp1-gpu-server -> $W/bf16-root/bin"
cargo install --locked --force --root "$W/bf16-root" --path sp1-gpu/crates/server 2>&1 \
  | grep -v -E "^\s+(Compiling|Downloaded|Downloading) " | tail -5
"$W/bf16-root/bin/sp1-gpu-server" --version
mkdir -p "$W/home-bf16/.sp1/bin"
ln -sf "$W/bf16-root/bin/sp1-gpu-server" "$W/home-bf16/.sp1/bin/sp1-gpu-server"
sha256sum "$W/bf16-root/bin/sp1-gpu-server"
stamp "done"
