#!/usr/bin/env bash
# red-team-standard-hash-2, 18:42Z: fp8-hopper-x4+blake3 / bf16-hopper-x4+blake3 H2 / R1 / R4 at x4-hopper-blake3 9a78cd68
# + rtsh overlay (/workspace/src via research pods sync); setup (py3.12 + torch cpu, rust, ligero-verify from the tree) first.
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
O=$OLDPWD/out; [ -d "$O" ] || O=$RESEARCH_RUN_DIR/out; mkdir -p $O; cd $S
for spec in "fp8-hopper-x4 12" "fp8-hopper-x4 24" "fp8-hopper-x4 6" "bf16-hopper-x4 24" "bf16-hopper-x4 48" "bf16-hopper-x4 12"; do set -- $spec
  $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation $1 --leaf blake3 --steps $2 --out $O/h2-$1-$2 > $O/h2-$1-$2.log 2>&1
  echo "h2 $1 steps $2 rc=$?"; tail -n 1 $O/h2-$1-$2.log | cut -c1-500
done
for rel in fp8-hopper-x4 bf16-hopper-x4; do
  $PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $B --out $O/r1-$rel --relation $rel --leaf blake3 --set-binding > $O/r1-$rel.log 2>&1
  echo "r1 $rel rc=$?"; grep -E "^(forgery|control)" $O/r1-$rel.log | cut -c1-400; tail -n 1 $O/r1-$rel.log
  $PY -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $B --out $O/r4-$rel --relation $rel --leaf blake3 --vus 3 > $O/r4-$rel.log 2>&1
  echo "r4 $rel rc=$?"; tail -n 4 $O/r4-$rel.log | cut -c1-400
done
echo E2E-DONE
