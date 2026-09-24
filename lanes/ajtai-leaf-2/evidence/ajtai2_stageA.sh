#!/usr/bin/env bash
# lane ajtai-leaf-2, pod side, one run: (1) Rust build + unit tests; (2) fixtures for fp8-ada+ajtai-n64 and
# bf16-hopper+ajtai-n128 (-> leaf.rs::PINS rows), Rust verify unpinned; (3) a scratch copy of the crate with the fixtures
# and the pins patched in: full `cargo test --release` (incl. the Ajtai fixture tests) -> the PINNED binary; (4) both
# gates; (5) bench arms at --pipeline 4 (fp8-ada bare / +hash / +ajtai-n64, bf16-hopper bare / +hash / +ajtai-n128), each
# rep-1 dump verified by the pinned Rust `batch`; (6) pytest leaf + conformance (fp8-ada and bf16-hopper) after the benches.
# usage: ajtai2_stageA.sh [ARM...]  (default: all six arms; "none" skips the benches)
set -uo pipefail
export PATH="$HOME/.cargo/bin:$PATH"
SRC=$(pwd)
PY=/workspace/venv312/bin/python
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
export TRITON_CACHE_DIR=/workspace/triton-cache
OUT="$RESEARCH_RUN_DIR"
RV0=/workspace/bin/ligero-verify-unpinned
RV=/workspace/bin/ligero-verify
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
fail=0
ARMS=("$@"); [ ${#ARMS[@]} -eq 0 ] && ARMS=(ajtai hash bare hajtai hhash hbare)

stage "cargo build --release (this tree) + cargo test (the Ajtai fixture tests are skipped: fixtures are written below)"
( cd "$SRC/backends/ligero-verify" && CARGO_TARGET_DIR=/workspace/cargo-target cargo build --release 2>&1 | tail -1 \
  && cp /workspace/cargo-target/release/ligero-verify "$RV0" && mkdir -p target/release && cp "$RV0" target/release/ligero-verify \
  && CARGO_TARGET_DIR=/workspace/cargo-target cargo test --release -- --skip ajtai_v5_ --skip ajtai_statement_ --skip ajtai_system_ 2>&1 \
     | grep -E "test result|FAILED|panicked" ) | tee "$OUT/cargo_unit.txt" || fail=1
grep -q FAILED "$OUT/cargo_unit.txt" && fail=1

for spec in "fp8-ada ajtai-n64" "bf16-hopper ajtai-n128"; do
  set -- $spec; REL=$1; LEAF=$2
  D="$OUT/fixtures/$REL-$LEAF"
  stage "fixture $REL+$LEAF (CPU, 4 VUs, proves 1,3, l >= 1024)"
  "$PY" -m backends.direct.ligero.leaf.fixtures --relation $REL --leaf $LEAF --out "$D" --n-vus 4 --mode interactive 2>&1 | tail -4
  [ "${PIPESTATUS[0]}" -eq 0 ] || fail=1
  stage "rust verify $REL+$LEAF fixture (unpinned build; the F6 key check runs)"
  "$RV0" verify --system "$D/system.bin" --statement "$D/sub_00.stmt" --proof "$D/sub_00.proof" --coins "$D/sub_00.coins" --allow-any-system --threads 4 > "$OUT/rust_verdict_$LEAF.json" 2>&1
  echo "rust rc=$?"; head -c 700 "$OUT/rust_verdict_$LEAF.json"; echo
  grep -q '"accepted":true' "$OUT/rust_verdict_$LEAF.json" || fail=1
done
( cd "$OUT/fixtures" && tar czf "$OUT/fixtures.tgz" . && ls -la "$OUT/fixtures.tgz" )

stage "scratch crate with the fixtures + pins -> full cargo test --release, pinned binary"
LV="$OUT/lv"
mkdir -p "$LV" && ( cd "$SRC/backends/ligero-verify" && tar cf - --exclude=./target . ) | ( cd "$LV" && tar xf - )
for d in fp8-ada-ajtai-n64 bf16-hopper-ajtai-n128; do
  mkdir -p "$LV/fixtures/$d" && cp "$OUT/fixtures/$d"/{system.bin,sub_00.stmt,sub_00.proof,sub_00.coins,manifest.json} "$LV/fixtures/$d/"
done
"$PY" - "$LV" "$OUT/fixtures" <<'PYEOF' | tee "$OUT/pins.txt"
import json, sys
lv, fx = sys.argv[1], sys.argv[2]
m = {n: json.load(open(f"{fx}/{d}/manifest.json")) for n, d in ((64, "fp8-ada-ajtai-n64"), (128, "bf16-hopper-ajtai-n128"))}
rs = open(f"{lv}/tests/relations.rs").read()
for n in (64, 128):
    rs = rs.replace(f"AJTAI{n}_SYS_ID", m[n]["rust"]["sys_id"]).replace(f"AJTAI{n}_TABLE_DIGEST", m[n]["rust"]["table_digest"])
open(f"{lv}/tests/relations.rs", "w").write(rs)
lf = open(f"{lv}/src/leaf.rs").read()
old = "pub static PINS: &[(&str, &str, &str, &str)] = &[];"
assert old in lf
new = "pub static PINS: &[(&str, &str, &str, &str)] = &[\n    " + m[64]["pins_row"] + "\n    " + m[128]["pins_row"] + "\n];"
open(f"{lv}/src/leaf.rs", "w").write(lf.replace(old, new))
print(new)
for n in (64, 128):
    print(n, "rows", m[n].get("system", {}).get("m"), "sys", m[n]["rust"]["sys_id"], "table", m[n]["rust"]["table_digest"])
PYEOF
( cd "$LV" && CARGO_TARGET_DIR=/workspace/cargo-target-lv cargo build --release 2>&1 | tail -1 \
  && cp /workspace/cargo-target-lv/release/ligero-verify "$RV" && mkdir -p target/release && cp "$RV" target/release/ligero-verify \
  && CARGO_TARGET_DIR=/workspace/cargo-target-lv cargo test --release 2>&1 | grep -E "^test .*(FAILED|ok)$|test result|panicked|assert" | grep -vE "^test .* ok$" ) \
  | tee "$OUT/cargo_full.txt" || fail=1
grep -qE "FAILED|panicked" "$OUT/cargo_full.txt" && fail=1
( cd "$LV" && diff -u "$SRC/backends/ligero-verify/src/leaf.rs" src/leaf.rs > "$OUT/leaf_rs.patch"; diff -u "$SRC/backends/ligero-verify/tests/relations.rs" tests/relations.rs > "$OUT/relations_rs.patch" ) || true
sha256sum "$RV" "$RV0"

stage "gate fp8-ada+ajtai-n64: 2048 VUs, batch 16384, cuda"
"$PY" -m backends.direct.ligero.run --relation fp8-ada gate-vu --vus 2048 --batch 16384 --device cuda --auth included-hash --leaf ajtai-n64 \
  --instances-cache /workspace/instances-cache --out "$OUT/gate_ajtai64.json" > "$OUT/gate_ajtai64.log" 2>&1
[ $? -eq 0 ] || fail=1; tail -3 "$OUT/gate_ajtai64.log"

stage "gate bf16-hopper+ajtai-n128: 512 VUs, batch 16384, cuda"
"$PY" -m backends.direct.ligero.run --relation bf16-hopper gate-vu --vus 512 --batch 16384 --device cuda --auth included-hash --leaf ajtai-n128 \
  --instances-cache /workspace/instances-cache --out "$OUT/gate_hopper_ajtai128.json" > "$OUT/gate_hopper_ajtai128.log" 2>&1
[ $? -eq 0 ] || fail=1; tail -3 "$OUT/gate_hopper_ajtai128.log"

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
flat = {}
def walk(d, pre=""):
    for k, v in d.items():
        if isinstance(v, dict): walk(v, pre + k + ".")
        elif not isinstance(v, list): flat[pre + k] = v
walk(r)
for k in sorted(flat):
    if any(s in k for s in ("t.total", "t_total", "total_s", "rows", "statement_bytes", "proof_bytes", "n_proofs", "split.", "hints")) and len(str(flat[k])) < 200:
        print(f"  {k} = {flat[k]}")
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
rc=$?; tail -15 "$OUT/pytest_leaf.log"; echo "pytest rc=$rc"; [ $rc -eq 0 ] || fail=1

stage "pytest: conformance with REL=bf16-hopper (ajtai-n128; not a gate of this run)"
VERITY_LEAF_CONFORMANCE_REL=bf16-hopper VERITY_LEAF_CONFORMANCE=ajtai-n128 timeout 1200 "$PY" -m pytest -q -p no:cacheprovider \
  backends/direct/ligero/leaf/conformance_test.py > "$OUT/pytest_conf_bf16.log" 2>&1
rc=$?; tail -15 "$OUT/pytest_conf_bf16.log"; echo "pytest bf16 rc=$rc"

stage "done"
if [ $fail -eq 0 ]; then echo STAGEA_OK; else echo STAGEA_FAILED; exit 1; fi
