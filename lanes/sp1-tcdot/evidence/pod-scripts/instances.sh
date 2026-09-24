#!/usr/bin/env bash
# Build the frozen bench-instances/v1 arrays on the pod (HF weight rows) and check them against the committed manifest.
set -euo pipefail
SRC=/workspace/sp1-tcdot/src
BI=/workspace/sp1-tcdot/bi
cd "$SRC"
export PYTHONPATH=packages/verity/src:backends/numerical/python
PY="$(command -v python3.12 || command -v python3)"
"$PY" --version
mkdir -p "$BI"
[ -f "$BI/vu-k1536.x.u16" ] || "$PY" -m verity_numerical.bench.instances build --out "$BI" --seeds fixtures/bench-instances/v1/seeds --procs "${PROCS:-6}" 2>&1 | tail -5
"$PY" - "$BI" fixtures/bench-instances/v1 <<'PYEOF'
import hashlib, json, sys
from pathlib import Path
bi, fz = Path(sys.argv[1]), Path(sys.argv[2])
man = json.loads((fz / "manifest.json").read_text())
print("manifest sha256", hashlib.sha256((fz / "manifest.json").read_bytes()).hexdigest())
for n, f in man["tiers"]["vu-k1536"]["files"].items():
    p = bi / n if (bi / n).exists() else fz / n
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    print(n, "OK" if got == f["sha256"] else f"MISMATCH {got}")
PYEOF
echo INSTANCES_DONE
