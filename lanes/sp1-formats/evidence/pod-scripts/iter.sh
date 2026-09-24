#!/usr/bin/env bash
# One hill-climb iteration on the dev tree /workspace/src: unit tests of the given modules, the scratch harness rebuilt,
# then SP1 execute of N VUs per format (cycles per VU).     iter.sh "tc_fp8 nvfp4" "fp8-ada fp8-hopper" [N=64]
set -euo pipefail
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
export CARGO_TARGET_DIR=/workspace/sp1-target
MODS=$1 FMTS=$2 N=${3:-64}
cd /workspace/src/backends/sp1
echo "=== $(date -u +%H:%M:%S) tests: $MODS"
cargo test --release -p veritor-zk-common --lib -- $MODS 2>&1 | grep -E "^test .*(ok|FAILED)|test result|panicked" | grep -v "ignored" || true
echo "=== $(date -u +%H:%M:%S) harness build"
bash /workspace/sp1-formats/scripts/cyc_build.sh > /workspace/sp1-formats/cyc_build.out 2>&1 || { tail -30 /workspace/sp1-formats/cyc_build.out; exit 1; }
for f in $FMTS; do
  echo "=== $(date -u +%H:%M:%S) execute $f n=$N"
  RUST_LOG=warn "$CARGO_TARGET_DIR"/release/sp1f-cyc-script /workspace/sp1-formats/inst/$f.bin "$N" 2>&1 | grep -E '^\{|cycles|mismatch|panic' | tail -3
done
echo "=== $(date -u +%H:%M:%S) done"
