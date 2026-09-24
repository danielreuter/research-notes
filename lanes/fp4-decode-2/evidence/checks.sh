#!/usr/bin/env bash
# lane fp4-decode-2: the tip's checks on the pod, in order: gate fp4-nvf4+poseidon2 (2048 VUs + negatives), gate bare fp4-nvf4,
# cargo test --release (ligero-verify, incl. the fp4-nvf4-hash fixture tests), pytest backends/direct/ligero (torch present).
#   $1 = gate VUs (2048), $2 = batch (16384), $3 = pytest wall limit in s (1500)
set -uo pipefail
VUS=${1:-2048}; BATCH=${2:-16384}; PYT=${3:-1500}
export PATH="/workspace/venv312/bin:$HOME/.cargo/bin:$PATH"
export PYTHONPATH="$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD"
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 OMP_NUM_THREADS=12
export CARGO_TARGET_DIR=/workspace/cargo-target
RD=${RESEARCH_RUN_DIR:-/tmp}
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv,noheader
echo "tree: $(cat .research-source.json 2>/dev/null | head -c 300)"
fail=0

gate() {  # $1 = relation, $2 = out stem
  echo "=== [$(date -u +%H:%M:%S)] gate $1"
  python -m backends.direct.ligero.run --relation "$1" gate-vu --vus "$VUS" --batch "$BATCH" --device cuda --target -128 \
    --instances-cache /workspace/instances-cache --instance-procs 16 --out "$RD/$2.json" 2>&1 | grep -v "^$" > "$RD/$2.log"
  local rc=${PIPESTATUS[0]}
  tail -3 "$RD/$2.log"
  python - "$RD/$2.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
pos = r["positives"]; neg = r["negatives"]
print("positives", len(pos), "ok", sum(p["ok"] for p in pos), "l", sorted({p["l"] for p in pos}))
print("negatives", len(neg), "rejected", sum(not n["accepted"] for n in neg), "failures", r["failures"])
PY
  echo "GATE_RC[$1]=$rc"
  [ "$rc" -eq 0 ] || fail=1
}
gate fp4-nvf4+poseidon2 gate_hashed
gate fp4-nvf4 gate_bare

echo "=== [$(date -u +%H:%M:%S)] cargo test --release (backends/ligero-verify)"
( cd backends/ligero-verify && cargo test --release 2>&1 ) > "$RD/cargo_test.log"
crc=$?
grep -E "^test result|FAILED|panicked|^test .* FAILED" "$RD/cargo_test.log" | head -40
echo "CARGO_TEST_RC=$crc"
[ "$crc" -eq 0 ] || fail=1
# the pinned build this tree's benches are verified with
( cd backends/ligero-verify && cargo build --release 2>&1 | tail -1 ) && cp "$CARGO_TARGET_DIR/release/ligero-verify" /workspace/bin/ligero-verify
sha256sum /workspace/bin/ligero-verify

echo "=== [$(date -u +%H:%M:%S)] pytest backends/direct/ligero (wall limit ${PYT}s)"
timeout "$PYT" python -m pytest -q -p no:cacheprovider backends/direct/ligero > "$RD/pytest.log" 2>&1
prc=$?
tail -25 "$RD/pytest.log"
echo "PYTEST_RC=$prc"
[ "$prc" -eq 0 ] || fail=1
echo "=== [$(date -u +%H:%M:%S)] done fail=$fail"
exit $fail
