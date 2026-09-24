#!/usr/bin/env bash
# lane ajtai-leaf-3 final pod stage: (1) build the G1-fixed ligero-verify + full cargo test; (2) both Ajtai gates (the Python
# verifier now runs the chain-key check); (3) the six bench arms at --pipeline 4 (Ajtai: expandable_segments + chunked chain
# test; if depth 4 does not fit in 24 GB, depth 3 then 2, recorded), each rep-1 dump through the new binary's `batch`.
set -uo pipefail
IN="$RESEARCH_RUN_DIR/inputs"
BASE="$RESEARCH_RUN_DIR"
export PATH="$HOME/.cargo/bin:$PATH"
SRC=$(pwd)
PY=/workspace/venv312/bin/python
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 TRITON_CACHE_DIR=/workspace/triton-cache
fail=0
git -C "$SRC" rev-parse HEAD 2>/dev/null | tee "$BASE/tree_sha.txt"
echo "=== [$(date -u +%H:%M:%S)] cargo build + full cargo test --release"
( cd "$SRC/backends/ligero-verify" && CARGO_TARGET_DIR=/workspace/cargo-target cargo build --release 2>&1 | tail -1 \
  && cp /workspace/cargo-target/release/ligero-verify "$BASE/ligero-verify" && mkdir -p target/release && cp "$BASE/ligero-verify" target/release/ligero-verify \
  && CARGO_TARGET_DIR=/workspace/cargo-target cargo test --release 2>&1 | grep -E "^test .*(FAILED|ok)$|test result|panicked" | grep -vE "^test .* ok$" ) \
  | tee "$BASE/cargo_full.txt"
grep -qE "FAILED|panicked" "$BASE/cargo_full.txt" && fail=1
sha256sum "$BASE/ligero-verify" | tee "$BASE/rv_sha256.txt"
for spec in "fp8-ada ajtai-n64" "bf16-hopper ajtai-n128"; do
  set -- $spec
  "$BASE/ligero-verify" system-digest --system "$SRC/backends/ligero-verify/fixtures/$1-$2/system.bin" | tee -a "$BASE/system_digests.jsonl"
done
echo "=== [$(date -u +%H:%M:%S)] gates"
"$PY" -m backends.direct.ligero.run --relation fp8-ada gate-vu --vus 2048 --batch 16384 --device cuda --auth included-hash --leaf ajtai-n64 \
  --instances-cache /workspace/instances-cache --out "$BASE/gate_ajtai64.json" > "$BASE/gate_ajtai64.log" 2>&1 || fail=1
tail -n 1 "$BASE/gate_ajtai64.log"
"$PY" -m backends.direct.ligero.run --relation bf16-hopper gate-vu --vus 512 --batch 16384 --device cuda --auth included-hash --leaf ajtai-n128 \
  --instances-cache /workspace/instances-cache --out "$BASE/gate_hopper_ajtai128.json" > "$BASE/gate_hopper_ajtai128.log" 2>&1 || fail=1
tail -n 1 "$BASE/gate_hopper_ajtai128.log"
fits() { grep -q '"batch_accepted": *true' "$1/bench/$2/rust_batch.json" 2>/dev/null; }
for arm in ajtai hajtai; do
  for depth in 4 3 2; do
    D="$BASE/p$depth"; mkdir -p "$D"
    echo "=== [$(date -u +%H:%M:%S)] $arm depth $depth"
    RESEARCH_RUN_DIR="$D" DEPTH=$depth ALLOC=expandable_segments:True LIGERO_CHAIN_ENC_CHUNK=16 LIGERO_CHAIN_TERM_CHUNK=32 \
      RV_OVERRIDE="$BASE/ligero-verify" bash "$IN/ajtai3_bench.sh" "$arm" 2>&1 | grep -vE "census|hashed \(|synthetic|committed:|config Config|warm-up" | tail -24
    if fits "$D" "$arm"; then echo "$arm $depth" >> "$BASE/ajtai_depth.txt"; break; fi
    [ $depth -eq 2 ] && fail=1
  done
done
echo "=== [$(date -u +%H:%M:%S)] controls at depth 4"
RESEARCH_RUN_DIR="$BASE/p4" DEPTH=4 RV_OVERRIDE="$BASE/ligero-verify" bash "$IN/ajtai3_bench.sh" bare hash hbare hhash 2>&1 \
  | grep -vE "census|hashed \(|synthetic|committed:|config Config|warm-up" | tail -80 || fail=1
for d in $(awk '{print $2}' "$BASE/ajtai_depth.txt" 2>/dev/null | sort -u); do
  [ "$d" = 4 ] && continue
  echo "=== [$(date -u +%H:%M:%S)] controls at the Ajtai fallback depth $d"
  RESEARCH_RUN_DIR="$BASE/p$d" DEPTH=$d RV_OVERRIDE="$BASE/ligero-verify" bash "$IN/ajtai3_bench.sh" bare hash hbare hhash 2>&1 \
    | grep -vE "census|hashed \(|synthetic|committed:|config Config|warm-up" | tail -80
done
echo "=== [$(date -u +%H:%M:%S)] done"
[ $fail -eq 0 ] && echo FINAL_OK || { echo FINAL_FAILED; exit 1; }
