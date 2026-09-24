#!/usr/bin/env bash
# verify-rs-5: build + test ligerito-verify at the lane tip, then rerun ligerito-relation-3's three live RO sessions with
# --session over the RO verifier's WHOLE store (5 c... challenge-stream + 45 s... sub-batch records, art:d04ee43a).
# Dumps: art:ef6b9392 live-7f35c223/dump_ro-zk (5aa5), live-6dda159a/dump_ro-zk (a1a0), live-6dda159a/dump_ro (f283).
# usage: vrs5.sh CRATE_DIR TARGET_DIR DUMPS_ROOT STORE_SESSIONS_DIR OUT_DIR
set -u
C=$1 T=$2 D=$3 S=$4 O=$5
mkdir -p "$O"
export CARGO_TARGET_DIR=$T
sha() { if command -v sha256sum >/dev/null; then sha256sum "$@"; else shasum -a 256 "$@"; fi; }
{ date -u +%Y-%m-%dT%H:%M:%SZ; hostname; (cd "$C" && git rev-parse HEAD 2>/dev/null || cat "$C/../../.research-source.json" 2>/dev/null); } > "$O/summary.txt"
(cd "$C" && cargo test --release) > "$O/cargo-test.log" 2>&1
echo "cargo test --release exit $?" >> "$O/summary.txt"
grep -E '^test result:|Running ' "$O/cargo-test.log" >> "$O/summary.txt"
(cd "$C" && cargo build --release) > "$O/cargo-build.log" 2>&1
echo "cargo build --release exit $?" >> "$O/summary.txt"
RV=$T/release/ligerito-verify
sha "$RV" >> "$O/summary.txt"
for x in live-7f35c223/dump_ro-zk:5aa5-zk live-6dda159a/dump_ro-zk:a1a0-zk live-6dda159a/dump_ro:f283-plain; do
  d=${x%%:*} t=${x##*:}
  "$RV" batch --dir "$D/$d" --json "$O/$t.json" --session "$S" > "$O/$t.log" 2>&1
  echo "$t exit $? $(grep -o '"claimed_union_log2":[^,]*' "$O/$t.json" | head -1) $(grep -o '"reason":"ok (session [^"]*' "$O/$t.json" | head -1)" >> "$O/summary.txt"
done
cat "$O/summary.txt"
