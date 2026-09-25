#!/usr/bin/env bash
# red-team-flock re-audit: flock b684b12 + flock-live (verity lane/flock-live @ a43f6254, files shipped with --send)
# + examples/rtf_live_attacks.rs (the flock-live bin up to `fn main()` + rtf_live_attacks_tail.rs).
# research run --on vy-red-team-flock --project verity --custody-r2 --custody-ttl 8h --campaign verity \
#   --send lib.rs --send flock-live.rs --send Cargo.toml --send rtf_live_attacks_tail.rs --send 20-live-attacks.sh \
#   -- bash inputs/20-live-attacks.sh
set -euo pipefail
IN=$(cd "$(dirname "$0")" && pwd); O=$IN/../out; mkdir -p "$O"
W=/workspace/red-team-flock; mkdir -p $W
command -v cc >/dev/null || { apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq build-essential pkg-config >/dev/null; }
[ -x $HOME/.cargo/bin/cargo ] || curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal >/dev/null
source $HOME/.cargo/env
cd $W; [ -d flock ] || git clone -q https://github.com/succinctlabs/flock.git
cd flock && git checkout -q b684b12
L=crates/flock-live; rm -rf $L; mkdir -p $L/src/bin $L/examples
cp $IN/Cargo.toml $L/; cp $IN/lib.rs $L/src/; cp $IN/flock-live.rs $L/src/bin/
sha256sum $L/src/lib.rs $L/src/bin/flock-live.rs $L/Cargo.toml | tee $O/flock-live-sha256.txt
{ sed '/^fn main() {/,$d' $IN/flock-live.rs; cat $IN/rtf_live_attacks_tail.rs; } > $L/examples/rtf_live_attacks.rs
grep -q '"crates/flock-live"' Cargo.toml || sed -i 's|    "crates/flock-transcript",|    "crates/flock-transcript",\n    "crates/flock-live",|' Cargo.toml
QUOTA=$(awk '$1 != "max" {print int($1 / $2)}' /sys/fs/cgroup/cpu.max 2>/dev/null); export RAYON_NUM_THREADS=${QUOTA:-$(nproc)}
cargo build --release -p flock-live --example rtf_live_attacks --bin flock-live 2>&1 | grep -E '^error|-->|Finished' | head -40
for n in ${RTF_NS:-4096}; do
  ./target/release/examples/rtf_live_attacks --n $n 2>&1 | grep -E '^RTF|panicked' | tee -a $O/attacks.tsv
  ./target/release/flock-live selftest --n $n 2>&1 | grep -E '^(NEG|SELFTEST)' | tee -a $O/selftest.tsv
done
