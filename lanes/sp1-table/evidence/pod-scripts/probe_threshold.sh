#!/bin/bash
# sp1-table (pod): exploratory shard-size probe, not a registered result.  B=512 (VUs 0..512), one rep each, SP1's
# ELEMENT_THRESHOLD at the default (402653184) and at the given multiples; prints each rep's shards, prove s, bytes, verify.
#   bash probe_threshold.sh [HI] [THRESHOLD...]      outputs: /workspace/sp1-table/probe/<threshold>.{jsonl,log}
set -uo pipefail
HI=${1:-512}; shift || true
TH=("${@:-402653184 805306368}")
H=/workspace/bin/veritor-zk-host-cuda-relation-bare
F=/workspace/src/fixtures/bench-instances/v1
M=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
O=/workspace/sp1-table/probe; mkdir -p "$O"
for t in ${TH[@]}; do
  rm -rf "$O/proofs-$t"
  ELEMENT_THRESHOLD=$t SP1_PROVER=cuda RUST_LOG=debug "$H" bare-prove --instances "$F" --manifest-sha256 $M --lo 0 --hi "$HI" \
      --vus-per-read 64 --out-dir "$O/proofs-$t" --reps 1 --warmup-vus 64 --mode core --skip-execute > "$O/$t.jsonl" 2> "$O/$t.log"
  echo "threshold $t rc $? : $(grep -E '^\{"event":"rep"' "$O/$t.jsonl" | cut -c1-260)"
  grep -m1 -E "Shard threshold" "$O/$t.log" | sed -E 's/\x1b\[[0-9;]*m//g' | cut -c1-160
done
