#!/usr/bin/env bash
# verify-po: build the frozen bench-instances/v1 arrays from MY tree's committed seeds (the BENCH_INSTANCES=1 stage of
# backends/direct/ligero/pod_bootstrap.sh: build, sha256 vs the committed manifest, symlink into fixtures/), then
# statement binding (04-stmt-binding.py) of the given B-Ligero results. bf16-ampere's frozen relation reads x / W from them.
#   bash 20-bench-instances-binding.sh ART...  -> /workspace/verify-po/binding-$ROUND.json
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
BI=/workspace/bench-instances/v1; FZ=/workspace/src/fixtures/bench-instances/v1
{
echo "=== [$(date -u +%H:%M:%S)] bench-instances/v1 build -> $BI"
[ -f "$BI/vu-k1536.x.u16" ] || $PY -m verity_numerical.bench.instances build --out "$BI" --seeds "$FZ/seeds" --procs 16 2>&1 | tail -3
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
echo "arrays rc=$?"
echo "=== [$(date -u +%H:%M:%S)] statement binding"
$PY $RESEARCH_RUN_DIR/inputs/04-stmt-binding.py "$@" > /workspace/verify-po/binding-${ROUND:-x}.json; echo "binding rc=$?"
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee /workspace/verify-po/binding-${ROUND:-x}.out
