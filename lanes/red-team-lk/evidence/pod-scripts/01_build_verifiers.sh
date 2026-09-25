#!/usr/bin/env bash
# red-team-lk: our own verity-gkr-verify builds.  main (backends/gkr/verifier identical at ab9573fd and 4bd6c54c) for fp8;
# lane/agkr-nvf4 b7cec878 (= 716ea008 = 679697a4 verifier: multi-column `public` line) for the fp4-nvf4 statements.
set -uo pipefail
source /workspace/env.sh
mkdir -p /workspace/red-team-lk/bin
cd /workspace/src/backends/gkr/verifier && CARGO_TARGET_DIR=/workspace/cargo-target-main cargo build --release 2>&1 | tail -2 \
  && cp /workspace/cargo-target-main/release/verity-gkr-verify /workspace/red-team-lk/bin/verify-main
cd /workspace/tree-b7cec878/backends/gkr/verifier && CARGO_TARGET_DIR=/workspace/cargo-target-nvf4 cargo build --release 2>&1 | tail -2 \
  && cp /workspace/cargo-target-nvf4/release/verity-gkr-verify /workspace/red-team-lk/bin/verify-nvf4
sha256sum /workspace/red-team-lk/bin/*
