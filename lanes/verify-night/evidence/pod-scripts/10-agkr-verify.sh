#!/usr/bin/env bash
# verify-night: independent verification of an A-GKR bench-result (agkr-table handoff 20260924T0644Z).
#   TREE=art:<run-files> TAG=<name> bash 10-agkr-verify.sh        (AWS_* read credential in the environment)
# Verifier: backends/gkr/verifier (verity-gkr-verify, no dependencies) from lane/agkr-table @ 53bd441b, shipped as
#   `git archive 53bd441b backends/gkr/verifier` to /workspace/agkr, built + tested here (BUILD=1).
# Statement: circuit.txt / epilogue.txt / chain.txt regenerated from MY tree (lane/verify-night @ 1b3c7be6,
#   backends/gkr/gpu/v2/export.py + epilogue_limbs.py, identical to 53bd441b's) and compared byte-for-byte;
#   public.bin compared with the frozen vu-k1536.y.u16 [0, 4096) of my tree's fixture (manifest 059103cf...).
set -uo pipefail
source /workspace/env.sh
export PATH=$HOME/.cargo/bin:$PATH CARGO_TARGET_DIR=/workspace/agkr-target
V=$CARGO_TARGET_DIR/release/verity-gkr-verify
O=/workspace/verify-night/agkr-$TAG; mkdir -p $O
{
if [ "${BUILD:-0}" = 1 ]; then
  echo "=== [$(date -u +%H:%M:%S)] build"
  (cd /workspace/agkr/backends/gkr/verifier && cargo build --release 2>&1 | tail -2 && cargo test --release 2>&1 | grep -E '^test result|FAILED|panicked' )
fi
sha256sum $V
echo "=== [$(date -u +%H:%M:%S)] fetch $TREE"
[ -d $O/tree ] || $PY -m research data fetch $TREE --to $O/tree | tail -1
D=$(dirname $(find $O/tree -name public.bin | head -1))/..; D=$(cd $D && pwd); echo "tree: $D"; ls $D $D/statement
sha256sum $D/proofs/*.bin
echo "=== [$(date -u +%H:%M:%S)] statement: regenerate Params-only files from my tree (8 VUs), compare"
rm -rf $O/regen
(cd /workspace/src/backends/gkr && PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH $PY -m gpu.v2.export export \
   --root /workspace/src/fixtures/bench-instances/v1 --tier vu-k1536 --hi 8 --out $O/regen --procs 4 > $O/regen.log 2>&1) || tail -5 $O/regen.log
for f in circuit.txt epilogue.txt chain.txt; do cmp $D/statement/$f $O/regen/$f && echo "$f identical ($(sha256sum < $O/regen/$f | cut -c1-16))"; done
$PY - "$D/statement" "$O/regen" <<'PYEOF'
import hashlib, json, struct, sys
from pathlib import Path
import numpy as np
from verity_numerical.bench.tables import FROZEN_INSTANCES
st, rg = Path(sys.argv[1]), Path(sys.argv[2])
a, b = json.loads((st / "manifest.json").read_text()), json.loads((rg / "manifest.json").read_text())
keys = ["field", "variant", "modulus", "unit_columns", "epilogue_columns", "chain_sha256", "tier", "steps", "epilogue",
        "root_manifest_sha256", "cross_check"]
print("manifest keys differing (Params / tier):", [k for k in keys if a.get(k) != b.get(k)] or "none",
      "| range", a.get("range"), "| rejected_at_witness", len(a.get("rejected_at_witness") or {}))
fz = Path("/workspace/src/fixtures/bench-instances/v1")
want = FROZEN_INSTANCES["first-campaign-target/2026-09-21"]
assert hashlib.sha256((fz / "manifest.json").read_bytes()).hexdigest() == want["manifest_sha256"]
y = np.frombuffer((fz / "vu-k1536.y.u16").read_bytes(), dtype="<u2")[want["range"][0]:want["range"][1]]
pb = (st / "public.bin").read_bytes()
n, c = struct.unpack("<QQ", pb[:16])
pub = np.frombuffer(pb[16:], dtype="<u4")
print(f"public.bin header ({n}, {c}); {pub.size} words; == frozen y[0:4096] widened: {n == 4096 and c == 1 and bool(np.array_equal(pub, y.astype(np.uint32)))}")
PYEOF
echo "=== [$(date -u +%H:%M:%S)] verify"
for r in $D/proofs/rep*.bin; do
  b=$(basename $r .bin)
  t0=$(date +%s.%N)
  $V verify --dir $D/statement --proof $r --vus 4096 --threads 15 --json $O/out_$b.json > $O/verify_$b.log 2>&1; rc=$?
  echo "$b rc=$rc wall=$($PY -c "import time; print(round(time.time()-$t0, 2))")s $(cat $O/out_$b.json 2>/dev/null | head -c 400)"
done
echo "=== [$(date -u +%H:%M:%S)] negatives (mutate --sample 64 on rep0)"
$V mutate --dir $D/statement --proof $D/proofs/rep0.bin --vus 4096 --threads 15 --sample 64 > $O/mutate.log 2>&1; echo "mutate rc=$?"
tail -4 $O/mutate.log
echo "=== [$(date -u +%H:%M:%S)] done"
} >> $O/verify.out 2>&1
