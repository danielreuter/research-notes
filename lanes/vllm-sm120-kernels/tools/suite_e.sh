#!/usr/bin/env bash
# The vLLM integration's test suite (quick tier, torch present) on the shipped tree (lane vllm-sm120-kernels); pytest-xdist over the pod's cores.
set -uo pipefail
T=$(pwd -P); OUT=$RESEARCH_RUN_DIR/out; mkdir -p "$OUT"
VENV=/workspace/venv312; PY=$VENV/bin/python
export PATH=$VENV/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
$PY -c "import xdist" 2>/dev/null || uv pip install --python "$PY" -q pytest-xdist
cd "$T/integrations/vllm"
$PY -m pytest -q -p no:cacheprovider -p no:warnings -n "${JOBS:-16}" -m "not slow" -rfE tests/ ${PYTEST_ARGS:-} > "$OUT/pytest.log" 2>&1
rc=$?
tail -40 "$OUT/pytest.log"
echo "SUITE-DONE rc=$rc"
