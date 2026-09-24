#!/usr/bin/env bash
# verifier-cost (pod vy-live2b-verifier-ro, CPU, EU-RO-1): verifier CPU of the two A-GKR Table 2 cells. A-GKR has no live
# protocol (its proofs carry SHA-256(transcript) coins for offline re-checking), so: build the independent Rust verifier
# (backends/gkr/verifier, no deps) from the shipped archive, fetch each cell's run_files (statement + proofs) from R2, re-verify
# every rep with rusage (user+sys of the child = verifier CPU s), register one verification-verdict/v1 per cell
# (refs.result = the cell, refs.proof = its run_files), --preserve.
#   research run --on vy-live2b-verifier-ro --project verity --send gkr-verifier.tar --send 04-agkr-verify.sh --send 04-agkr-verify.py \
#     --env AWS_...=.. -- bash inputs/04-agkr-verify.sh
set -euo pipefail
W=/workspace/verifier-cost; OUT=${RESEARCH_RUN_DIR:-$PWD}; IN=$OUT/inputs
export RESEARCH_STORE_CONFIG=$W/store.toml RESEARCH_STORE=$W/store PATH=$HOME/.cargo/bin:$PATH CARGO_TARGET_DIR=$W/target
rm -rf $W/gkr-src && mkdir -p $W/gkr-src && tar xf $IN/gkr-verifier.tar -C $W/gkr-src
( cd $W/gkr-src/backends/gkr/verifier && nice -n 10 cargo build --release 2>&1 | tail -3 )
cp $CARGO_TARGET_DIR/release/verity-gkr-verify $W/verity-gkr-verify
sha256sum $W/verity-gkr-verify | tee $OUT/verifier.sha256
python3 $IN/04-agkr-verify.py "$W/verity-gkr-verify" "$(cat $IN/gkr-verifier.commit 2>/dev/null || echo unknown)"
