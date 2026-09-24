#!/usr/bin/env bash
# lane ajtai-leaf-2, pod side, stage B (the tree carries the pins + fixtures since 107f40b, the hashed pipelined prover
# since 1cf9178): (1) cargo build --release + FULL cargo test (Ajtai fixture tests included) -> the pinned binary;
# (2) both Ajtai gates; (3) bench arms at --pipeline 4 -- now pipelined for +hash / +ajtai too -- each rep-1 dump verified
# by the pinned Rust `batch`; (4) pytest leaf + conformance (fp8-ada, and bf16-hopper for ajtai-n128).
# usage: ajtai2_stageB.sh [ARM...]  (default: all six arms; "none" skips the benches)
set -uo pipefail
export PATH="$HOME/.cargo/bin:$PATH"
SRC=$(pwd)
PY=/workspace/venv312/bin/python
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
export TRITON_CACHE_DIR=/workspace/triton-cache
OUT="$RESEARCH_RUN_DIR"
RV=/workspace/bin/ligero-verify
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
fail=0
ARMS=("$@"); [ ${#ARMS[@]} -eq 0 ] && ARMS=(ajtai hash bare hajtai hhash hbare)
git -C "$SRC" rev-parse HEAD 2>/dev/null | tee "$OUT/tree_sha.txt"

stage "cargo build --release + full cargo test --release (pins + Ajtai fixtures in the tree)"
( cd "$SRC/backends/ligero-verify" && CARGO_TARGET_DIR=/workspace/cargo-target cargo build --release 2>&1 | tail -1 \
  && cp /workspace/cargo-target/release/ligero-verify "$RV" && mkdir -p target/release && cp "$RV" target/release/ligero-verify \
  && CARGO_TARGET_DIR=/workspace/cargo-target cargo test --release 2>&1 | grep -E "^test .*(FAILED|ok)$|test result|panicked" | grep -vE "^test .* ok$" ) \
  | tee "$OUT/cargo_full.txt" || fail=1
grep -qE "FAILED|panicked" "$OUT/cargo_full.txt" && fail=1
grep -c "test result: ok" "$OUT/cargo_full.txt"
sha256sum "$RV" | tee "$OUT/rv_sha256.txt"
for spec in "fp8-ada ajtai-n64" "bf16-hopper ajtai-n128"; do
  set -- $spec
  "$RV" system-digest --system "$SRC/backends/ligero-verify/fixtures/$1-$2/system.bin" | tee -a "$OUT/system_digests.jsonl"
done

stage "gate fp8-ada+ajtai-n64: 2048 VUs, batch 16384, cuda"
"$PY" -m backends.direct.ligero.run --relation fp8-ada gate-vu --vus 2048 --batch 16384 --device cuda --auth included-hash --leaf ajtai-n64 \
  --instances-cache /workspace/instances-cache --out "$OUT/gate_ajtai64.json" > "$OUT/gate_ajtai64.log" 2>&1
[ $? -eq 0 ] || fail=1; tail -n 1 "$OUT/gate_ajtai64.log"

stage "gate bf16-hopper+ajtai-n128: 512 VUs, batch 16384, cuda"
"$PY" -m backends.direct.ligero.run --relation bf16-hopper gate-vu --vus 512 --batch 16384 --device cuda --auth included-hash --leaf ajtai-n128 \
  --instances-cache /workspace/instances-cache --out "$OUT/gate_hopper_ajtai128.json" > "$OUT/gate_hopper_ajtai128.log" 2>&1
[ $? -eq 0 ] || fail=1; tail -n 1 "$OUT/gate_hopper_ajtai128.log"

COMMON="bench-vu --zk --mode interactive --batch 16384 --total-vus 4096 --reps 3 --device cuda --instances-cache /workspace/instances-cache --dump-reps 1 --pipeline 4"
for arm in "${ARMS[@]}"; do
  case "$arm" in
    none)     continue ;;
    bare)     REL=fp8-ada;     EXTRA="" ;;
    hash)     REL=fp8-ada;     EXTRA="--auth included-hash" ;;
    ajtai)    REL=fp8-ada;     EXTRA="--auth included-hash --leaf ajtai-n64" ;;
    hbare)    REL=bf16-hopper; EXTRA="" ;;
    hhash)    REL=bf16-hopper; EXTRA="--auth included-hash" ;;
    hajtai)   REL=bf16-hopper; EXTRA="--auth included-hash --leaf ajtai-n128" ;;
    *) echo "unknown arm $arm"; fail=1; continue ;;
  esac
  D="$OUT/bench/$arm"; mkdir -p "$D"
  stage "bench $arm: $REL $COMMON $EXTRA"
  "$PY" -m backends.direct.ligero.run --relation $REL $COMMON $EXTRA --dump-dir "$D/proofs" --out "$D/result.json" > "$D/bench.log" 2>&1
  rc=$?; echo "rc=$rc"; [ $rc -eq 0 ] || { fail=1; tail -20 "$D/bench.log"; }
  "$PY" - "$D/result.json" <<'PYEOF'
import json, sys
r = json.load(open(sys.argv[1]))
for m in r["measurements"]:
    n = m["name"]
    if n in ("t.total", "rows_per_unit", "prove_wall", "relation.hash.auth_openings_seconds") or n.startswith("split."):
        print(f"  {n:44s} {m['value']:.4f}" if isinstance(m["value"], float) else f"  {n:44s} {m['value']}")
print("  pipeline", r["workload_fingerprint"].get("pipeline"))
PYEOF
  REP=$(ls -d "$D"/proofs/rep* 2>/dev/null | head -1)
  if [ -n "$REP" ]; then
    stage "rust batch verify of the $arm dump (pinned build)"
    "$RV" batch --system "$D/proofs/system.bin" --dir "$REP" --jobs 8 --threads 4 --json "$D/rust_batch.json" > "$D/rust_batch.log" 2>&1
    "$PY" - "$D/rust_batch.json" <<'PYEOF'
import json, sys
j = json.load(open(sys.argv[1]))
print({k: j[k] for k in j if k in ("accepted", "rejected", "batch_accepted", "pinned_relation", "system_pinned")})
PYEOF
    grep -q '"batch_accepted": *true' "$D/rust_batch.json" || fail=1
  else
    echo "no dump"; fail=1
  fi
done

stage "pytest: leaf + conformance fp8-ada (ajtai-n64, ajtai-n128) + hashchain + relations + chain + auth (torch, CPU)"
VERITY_LEAF_CONFORMANCE=ajtai-n64,ajtai-n128 timeout 1500 "$PY" -m pytest -q -p no:cacheprovider \
  backends/direct/ligero/leaf backends/direct/ligero/leaf_test.py backends/direct/ligero/hashchain_test.py backends/direct/ligero/relations_test.py \
  backends/direct/ligero/chain_test.py tests/test_ligero_auth.py > "$OUT/pytest_leaf.log" 2>&1
rc=$?; tail -n 8 "$OUT/pytest_leaf.log"; echo "pytest rc=$rc"; [ $rc -eq 0 ] || fail=1

stage "pytest: conformance with REL=bf16-hopper (ajtai-n128)"
VERITY_LEAF_CONFORMANCE_REL=bf16-hopper VERITY_LEAF_CONFORMANCE=ajtai-n128 timeout 1200 "$PY" -m pytest -q -p no:cacheprovider \
  backends/direct/ligero/leaf/conformance_test.py > "$OUT/pytest_conf_bf16.log" 2>&1
rc=$?; tail -n 8 "$OUT/pytest_conf_bf16.log"; echo "pytest bf16 rc=$rc"; [ $rc -eq 0 ] || fail=1

stage "done"
if [ $fail -eq 0 ]; then echo STAGEB_OK; else echo STAGEB_FAILED; exit 1; fi
