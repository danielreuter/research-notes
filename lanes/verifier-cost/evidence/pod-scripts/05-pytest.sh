#!/usr/bin/env bash
# Run the bench + research store test suites for the lane's tip on the verifier pod.
#   research run --on vy-live2b-verifier-ro --project verity [--source .] --send 05-pytest.sh [--send FILE ...] \
#     -- env -u PYTHONPATH bash inputs/05-pytest.sh <tree-sha> [REL/PATH=inputs/FILE ...]
# <tree-sha>: a source tree already shipped to /workspace/research/src/; REL/PATH=inputs/FILE overlays a sent file on a copy.
set -u
RUN=$PWD
SRC=/workspace/research/src/$1; shift
[ -d "$SRC" ] || { echo "no shipped source $SRC"; exit 2; }
if [ $# -gt 0 ]; then
  T=/workspace/verifier-cost/src-overlay; rm -rf $T; cp -a "$SRC" $T; SRC=$T
  for kv in "$@"; do cp "$RUN/${kv#*=}" "$SRC/${kv%%=*}"; echo "overlay ${kv%%=*} $(sha256sum "$SRC/${kv%%=*}" | cut -c1-12)"; done
fi
cd "$SRC"
PY=/workspace/venv312/bin/python
export PYTHONPATH="$PWD/tools/research/src:$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/backends/sp1/python:$PWD/integrations/vllm"
$PY -c "import pytest, sys; print('pytest', pytest.__version__, sys.version)" || exit 2
# matplotlib (bench.plots, imported by test_ledger) into a lane-local dir, not the shared venv
D=/workspace/verifier-cost/pydeps
$PY -c "import sys; sys.path.insert(0, '$D'); import matplotlib" 2>/dev/null || $PY -m pip install -q --target $D matplotlib 2>/dev/null \
  || PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" uv pip install -q --python $PY --target $D matplotlib
export PYTHONPATH="$PYTHONPATH:$D"
$PY -m pytest -q -p no:cacheprovider backends/numerical/tests/bench 2>&1 | tail -40
echo "bench rc=${PIPESTATUS[0]}"
$PY -m pytest -q -p no:cacheprovider tools/research/tests -k "vocab or label" 2>&1 | tail -20
echo "research rc=${PIPESTATUS[0]}"
