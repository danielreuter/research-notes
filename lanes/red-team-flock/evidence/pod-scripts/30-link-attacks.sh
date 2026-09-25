#!/usr/bin/env bash
# red-team-flock third audit: flock b684b12 + flock-link-b684b12.patch + backends/flock/live (verity lane/flock-link
# @ 4b560b2b, files shipped with --send) + examples/rtf_link_attacks.rs (flock-link bin up to `fn main()` +
# rtf_link_attacks_tail.rs); runs the attacks and flock-link's own selftest.
set -euo pipefail
IN=$(cd "$(dirname "$0")" && pwd); O=$IN/../out; mkdir -p "$O"
W=/workspace/red-team-flock; mkdir -p $W
command -v cc >/dev/null || { apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq build-essential pkg-config >/dev/null; }
[ -x $HOME/.cargo/bin/cargo ] || curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal >/dev/null
source $HOME/.cargo/env
cd $W; [ -d flock ] || git clone -q https://github.com/succinctlabs/flock.git
cd flock && git checkout -q b684b12 && git checkout -q -- . && git apply $IN/flock-link-b684b12.patch
L=crates/flock-live; rm -rf $L; mkdir -p $L/src/bin $L/examples
cp $IN/Cargo.toml $L/; cp $IN/lib.rs $L/src/; cp $IN/flock-link.rs $IN/flock-live.rs $L/src/bin/
sha256sum $IN/flock-link-b684b12.patch $L/src/lib.rs $L/src/bin/*.rs | tee $O/inputs-sha256.txt
{ sed '/^fn main() {/,$d' $IN/flock-link.rs; cat $IN/rtf_link_attacks_tail.rs; } > $L/examples/rtf_link_attacks.rs
grep -q '"crates/flock-live"' Cargo.toml || sed -i 's|    "crates/flock-transcript",|    "crates/flock-transcript",\n    "crates/flock-live",|' Cargo.toml
QUOTA=$(awk '$1 != "max" {print int($1 / $2)}' /sys/fs/cgroup/cpu.max 2>/dev/null); export RAYON_NUM_THREADS=${QUOTA:-$(nproc)}
cargo build --release -p flock-live --example rtf_link_attacks --bin flock-link 2>&1 | grep -E '^error|-->|Finished' | head -40
for v in ${RTF_VUS:-8 64}; do
  ./target/release/examples/rtf_link_attacks --vus $v 2>&1 | grep -E '^RTF|panicked' | tee -a $O/attacks.tsv
  ./target/release/flock-link selftest --vus $v 2>&1 | grep -E '^(NEG|SELFTEST)' | tee -a $O/selftest.tsv
done
