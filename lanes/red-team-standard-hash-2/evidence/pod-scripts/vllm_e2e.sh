#!/usr/bin/env bash
# red-team-standard-hash-2, 20:50Z: vllm-v1 statement review, end to end at lane/b-ligero-vllm-v1 acd50fec + rtsh overlay
# (/workspace/src): setup, the lane's own tests (python + cargo), H2 / R1 / R4 and the vllm-v1 port attacks on fp8-ada-x4 and
# fp8-hopper-x4 +vllm-v1.
set -uo pipefail
cd /workspace
pip3 -q install uv
[ -x venv312/bin/python ] || uv venv -q -p 3.12 venv312
VIRTUAL_ENV=/workspace/venv312 uv pip install -q --index-url https://download.pytorch.org/whl/cpu torch
VIRTUAL_ENV=/workspace/venv312 uv pip install -q numpy blake3 pytest pytest-timeout
command -v cargo >/dev/null || (curl -sSf https://sh.rustup.rs | sh -s -- -y -q --profile minimal)
export PATH="$HOME/.cargo/bin:$PATH"
S=/workspace/src; B=/workspace/bin/ligero-verify; PY=/workspace/venv312/bin/python
(cd $S && CARGO_TARGET_DIR=/workspace/cargo-target cargo build -q --release --manifest-path backends/ligero-verify/Cargo.toml 2>&1 | grep -v warning | tail -2)
mkdir -p /workspace/bin && cp /workspace/cargo-target/release/ligero-verify $B && sha256sum $B; head -4 $S/.research-source.json
export PYTHONPATH=$S/packages/verity/src:$S/backends/numerical/python:$S/tools/research/src:$S OMP_NUM_THREADS=4 VY_CPU_THREADS=4
O=$RESEARCH_RUN_DIR/out; mkdir -p $O; cd $S
echo "== lane tests"
(cd $S/backends/ligero-verify && CARGO_TARGET_DIR=/workspace/cargo-target cargo test -q --release vllm 2>&1 | grep -E "test result|FAILED|panicked" | head -5)
LIGERO_VERIFY=$B $PY -m pytest -q -x backends/direct/ligero/vllm_tree_test.py backends/direct/ligero/leaf/vllm_v1_test.py 2>&1 | tail -n 3
for rel in fp8-ada-x4 fp8-hopper-x4; do
  $PY -m backends.direct.ligero.redteam.rtsh_vllm_e2e --bin $B --relation $rel --out $O/vllm-$rel > $O/vllm-$rel.log 2>&1
  echo "vllm-attacks $rel rc=$?"; grep -E "^(honest|ctx|y-|bare|port|count)|^\{" $O/vllm-$rel.log | cut -c1-420
  for s in 12 24 6; do
    $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation $rel --leaf vllm-v1 --steps $s --out $O/h2-$rel-$s > $O/h2-$rel-$s.log 2>&1
    echo "h2 $rel steps $s rc=$?"; tail -n 1 $O/h2-$rel-$s.log | cut -c1-450
  done
  $PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $B --out $O/r1-$rel --relation $rel --leaf vllm-v1 --set-binding > $O/r1-$rel.log 2>&1
  echo "r1 $rel rc=$?"; grep -E "^(forgery|control)" $O/r1-$rel.log | cut -c1-400; tail -n 1 $O/r1-$rel.log
  $PY -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $B --out $O/r4-$rel --relation $rel --leaf vllm-v1 --vus 3 > $O/r4-$rel.log 2>&1
  echo "r4 $rel rc=$?"; tail -n 4 $O/r4-$rel.log | cut -c1-400
done
echo E2E-DONE
