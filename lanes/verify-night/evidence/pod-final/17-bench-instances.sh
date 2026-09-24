#!/usr/bin/env bash
# verify-night: build the frozen bench-instances/v1 operand arrays (x, W: built, not committed) from MY tree's recipe and the
# committed seeds, as pod_bootstrap.sh's BENCH_INSTANCES stage does: build into /workspace/bench-instances/v1, refuse unless every
# built array's sha256 equals the COMMITTED manifest.json's, then symlink them into /workspace/src/fixtures/bench-instances/v1
# (the committed manifest.json is never rewritten). Then the binding check (08) for the A100 results that need them.
#   bash 17-bench-instances.sh ART...        (AWS_* read credential in the environment, for 08's fetches)
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
BI=/workspace/bench-instances/v1; FZ=/workspace/src/fixtures/bench-instances/v1; O=/workspace/verify-night
{
echo "=== [$(date -u +%H:%M:%S)] build"
[ -f "$BI/vu-k1536.x.u16" ] || $PY -m verity_numerical.bench.instances build --out "$BI" --seeds "$FZ/seeds" --procs 12 2>&1 | tail -5
$PY - "$BI" "$FZ" <<'PYEOF'
import json, sys
from pathlib import Path
from verity_numerical.bench.instances import sha256_file
bi, fz = Path(sys.argv[1]), Path(sys.argv[2])
man = json.loads((fz / "manifest.json").read_text())
built = {n: f for t in man["tiers"].values() for n, f in t.get("files", {}).items() if not f.get("committed")}
bad = [n for n, f in built.items() if not (bi / n).is_file() or sha256_file(bi / n) != f["sha256"]]
assert not bad, f"rebuilt arrays differ from the committed manifest's sha256: {bad}"
for n in built:
    dst = fz / n
    if dst.is_symlink() or not dst.exists():
        dst.unlink(missing_ok=True)
        dst.symlink_to(bi / n)
print(f"{len(built)} built arrays match the committed manifest; linked into {fz}")
PYEOF
echo "=== [$(date -u +%H:%M:%S)] binding"
$PY $O/08-stmt-binding.py "$@" > $O/binding-a100.json
echo "rc=$?"
echo "=== [$(date -u +%H:%M:%S)] done"
} > $O/bench-instances.out 2>&1
