#!/bin/bash
# merged tree c9cc381+: the fixed fp4 relation_test + the new chain_test + witness_device_test; fp4-nvf4 bench-vu under BOTH impls
set -u
export PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
export PYTHONPATH=packages/verity/src:backends/numerical/python:.
PY=/workspace/venv312/bin/python
RD=$RESEARCH_RUN_DIR
cat .research-source.json 2>/dev/null
echo "=== pytest fp4/relation_test.py chain_test.py witness_device_test.py"
echo "(pytest recheck done in r20260923-041818-ac51: 15 passed)"
echo "### pytest-recheck: ${PIPESTATUS[0]}"
for impl in device legacy; do
  echo "=== fp4-nvf4 bench-vu --impl $impl (170 VUs, 1 rep)"
  $PY -m backends.direct.ligero.run --relation fp4-nvf4 bench-vu --impl $impl --zk --mode interactive --batch 4096 --total-vus 170 --target -128 --device cuda --reps 1 \
      --run-id "$RESEARCH_RUN_ID-fp4-$impl" --out "$RD/result_fp4_$impl.json" --dump-dir "$RD/proofs_fp4_$impl" --dump-reps 1 2>&1 | grep -v Warning | tail -3
  echo "### bench-fp4-$impl: ${PIPESTATUS[0]}"
  $PY -m backends.direct.ligero.serialize verify-batch --dir "$RD/proofs_fp4_$impl/rep1" --target-bits 128 --json "$RD/pyverify_fp4_$impl.json" 2>&1 | tail -1
  echo "### pyverify-fp4-$impl: ${PIPESTATUS[0]}"
done
$PY - "$RD" <<'PYEOF'
import json, sys
rd = sys.argv[1]
for impl in ("device", "legacy"):
    r = json.load(open(f"{rd}/result_fp4_{impl}.json")); ms = {m["name"]: m["value"] for m in r["measurements"]}
    d = r["validation"]["evidence"]["dumps"]
    print(impl, "software.backend", r["workload_fingerprint"]["software"]["backend"].get("impl"), r["workload_fingerprint"]["software"]["backend"].get("hints"),
          "t.total", round(ms["t.total"], 4), "witness", ms.get("split.witness_torch_seconds"), "cold verify", d["accepted"], "/", d["total"])
PYEOF
sha256sum $RD/proofs_fp4_*/system.bin
find "$RD" -path '*/proofs_*' -name '*.proof' -delete
echo RECHECK_DONE
