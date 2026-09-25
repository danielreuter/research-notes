#!/usr/bin/env bash
# red-team-standard-hash-2, 20:00Z: bf16-ampere-x4+sha256 H2 / R1 / R4 at main 7da00370 + rtsh overlay (/workspace/src);
# setup: py3.12 + torch cpu, rust, ligero-verify from the tree, the frozen bench-instances/v1 arrays rebuilt from the seeds.
set -uo pipefail
cd /workspace
pip3 -q install uv
[ -x venv312/bin/python ] || uv venv -q -p 3.12 venv312
VIRTUAL_ENV=/workspace/venv312 uv pip install -q --index-url https://download.pytorch.org/whl/cpu torch
VIRTUAL_ENV=/workspace/venv312 uv pip install -q numpy blake3 pytest
command -v cargo >/dev/null || (curl -sSf https://sh.rustup.rs | sh -s -- -y -q --profile minimal)
export PATH="$HOME/.cargo/bin:$PATH"
S=/workspace/src; B=/workspace/bin/ligero-verify; PY=/workspace/venv312/bin/python
(cd $S && CARGO_TARGET_DIR=/workspace/cargo-target cargo build -q --release --manifest-path backends/ligero-verify/Cargo.toml 2>&1 | grep -v warning | tail -2)
mkdir -p /workspace/bin && cp /workspace/cargo-target/release/ligero-verify $B && sha256sum $B; head -4 $S/.research-source.json
export PYTHONPATH=$S/packages/verity/src:$S/backends/numerical/python:$S/tools/research/src:$S OMP_NUM_THREADS=4 VY_CPU_THREADS=4
BI=/workspace/bench-instances/v1; FZ=$S/fixtures/bench-instances/v1
[ -f "$BI/vu-k1536.x.u16" ] || $PY -m verity_numerical.bench.instances build --out "$BI" --seeds "$FZ/seeds" --procs 4 2>&1 | tail -3
$PY - "$BI" "$FZ" <<'PYEOF'
import json, sys
from pathlib import Path
from verity_numerical.bench.instances import sha256_file
bi, fz = Path(sys.argv[1]), Path(sys.argv[2])
man = json.loads((fz / "manifest.json").read_text())
built = {n: f for t in man["tiers"].values() for n, f in t.get("files", {}).items() if not f.get("committed")}
bad = [n for n, f in built.items() if not (bi / n).is_file() or sha256_file(bi / n) != f["sha256"]]
assert not bad, f"rebuilt arrays differ from the committed manifest: {bad}"
for n in built:
    dst = fz / n
    if not dst.exists():
        dst.symlink_to(bi / n)
print("bench-instances/v1 rebuilt, sha256 = manifest:", len(built), "files")
PYEOF
O=$RESEARCH_RUN_DIR/out; mkdir -p $O; cd $S
for s in 24 12 48; do
  $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation bf16-ampere-x4 --leaf sha256 --steps $s --out $O/h2-$s > $O/h2-$s.log 2>&1
  echo "h2 bf16-ampere-x4 steps $s rc=$?"; tail -n 1 $O/h2-$s.log | cut -c1-500
done
$PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $B --out $O/r1 --relation bf16-ampere-x4 --leaf sha256 --set-binding > $O/r1.log 2>&1
echo "r1 rc=$?"; grep -E "^(forgery|control)" $O/r1.log | cut -c1-400; tail -n 1 $O/r1.log
$PY -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $B --out $O/r4 --relation bf16-ampere-x4 --leaf sha256 --vus 3 > $O/r4.log 2>&1
echo "r4 rc=$?"; tail -n 4 $O/r4.log | cut -c1-400
echo E2E-DONE
