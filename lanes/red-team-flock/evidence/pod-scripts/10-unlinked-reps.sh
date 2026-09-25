#!/usr/bin/env bash
# red-team-flock: build flock b684b12 + examples/rtf_unlinked_reps.rs on a CPU pod and run it.
# research run --on vy-red-team-flock --project verity --custody-r2 --custody-ttl 8h \
#   --send rtf_unlinked_reps.rs --send 10-unlinked-reps.sh -- bash inputs/10-unlinked-reps.sh
set -euo pipefail
IN=$(cd "$(dirname "$0")" && pwd)
W=/workspace/red-team-flock; mkdir -p "$W" out
command -v cargo >/dev/null || { curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal >/dev/null; }
. "$HOME/.cargo/env" 2>/dev/null || true
command -v cc >/dev/null || { apt-get update -qq && apt-get install -y -qq build-essential pkg-config >/dev/null; }
cd "$W"
[ -d flock ] || git clone -q https://github.com/succinctlabs/flock.git
cd flock && git checkout -q b684b12 && git log --oneline -1 | tee "$OLDPWD/../out/flock-rev.txt" 2>/dev/null || true
cp "$IN/rtf_unlinked_reps.rs" crates/flock-prover/examples/ 2>/dev/null || { mkdir -p crates/flock-prover/examples; cp "$IN/rtf_unlinked_reps.rs" crates/flock-prover/examples/; }
lscpu | grep -E "Model name|^CPU\(s\)" || true
export RAYON_NUM_THREADS=${RAYON_NUM_THREADS:-16}
time cargo build --release -p flock-prover --example rtf_unlinked_reps 2>&1 | tail -5
for n in ${RTF_NS:-4096}; do
  RTF_N=$n ./target/release/examples/rtf_unlinked_reps | tee -a "$IN/../out/rtf.tsv"
done
