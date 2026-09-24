#!/bin/bash
# sp1-table (pod): the verify-night procedure on the pod, from the committed tree the research run executed
# (/workspace/research/src/<sha>, READY), in a FRESH target dir: CPU-only relation-bare host, `info` (elf_sha256, vk_hash),
# then `verify --statement` of one run's proofs.   repro_verify.sh SHA RUN_ID
set -uo pipefail
sha=$1 rid=$2
source ~/.cargo/env
S=/workspace/research/src/$sha/backends/sp1
T=/workspace/sp1-target-repro-$sha
rm -rf "$T"
cd "$S" && CARGO_TARGET_DIR=$T cargo build --release --locked -p veritor-zk-host --features relation-bare 2>&1 | tail -3
SP1_PROVER=cpu RUST_LOG=error $T/release/veritor-zk-host info | tail -1
D=/workspace/research/runs/$rid/proofs
sha256sum $D/*
for p in $D/proof-rep*.bin; do
  SP1_PROVER=cpu RUST_LOG=error $T/release/veritor-zk-host verify --proof $p --statement $D/statement.bin 2>/dev/null | tail -1 | cut -c1-400
done
