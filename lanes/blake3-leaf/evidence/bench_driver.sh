#!/usr/bin/env bash
# lane blake3-leaf: fp8-ada-x4+blake3 vs the controls on the same pod (4090), interactive ZK, 4096 VUs, 3 reps, local coins
set -u
cd /workspace/src
export PYTHONPATH=/workspace/src/packages/verity/src:/workspace/src/backends/numerical/python:/workspace/src/tools/research/src:/workspace/src
PY=/workspace/venv312/bin/python
RD=/workspace/bench; mkdir -p $RD
COMMON="bench-vu --zk --mode interactive --total-vus 4096 --reps 3 --target -128 --device cuda --instance-procs 16 --instances-cache /workspace/instances-cache"
run() { name=$1; shift; echo "=== [$(date -u +%H:%M:%S)] $name: $*"; mkdir -p $RD/$name; \
  $PY -m backends.direct.ligero.run "$@" --out $RD/$name/result.json --dump-dir $RD/$name/proofs --dump-reps 1 > $RD/$name/log.txt 2>&1; \
  echo "rc=$? [$(date -u +%H:%M:%S)]"; $PY - "$RD/$name/result.json" <<'PYEOF'
import json, sys
r = json.load(open(sys.argv[1]))
def g(d, *ks):
    for k in ks:
        d = d.get(k, {}) if isinstance(d, dict) else {}
    return d if d != {} else None
t = r.get("t") or r.get("measurements", {}).get("t") or {}
print("t:", json.dumps(t)[:600])
for k in ("fingerprint", "relation", "rows_per_unit", "peak_device_memory_bytes", "sys"):
    if k in r: print(k, json.dumps(r[k])[:400])
PYEOF
}
run blake3_b4096 --relation fp8-ada-x4+blake3 $COMMON --auth included-hash --batch 4096
run fp8ada_bare_b16384 --relation fp8-ada $COMMON --batch 16384 --pipeline 1
run fp8ada_p2_b16384 --relation fp8-ada $COMMON --auth included-hash --batch 16384
run fp8adax4_bare_b4096 --relation fp8-ada-x4 $COMMON --batch 4096 --pipeline 1
run blake3_b8192 --relation fp8-ada-x4+blake3 $COMMON --auth included-hash --batch 8192
echo ALL_DONE
