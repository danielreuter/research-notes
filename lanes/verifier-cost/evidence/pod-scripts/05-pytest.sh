#!/usr/bin/env bash
# Run the bench + research store test suites for the lane's tip on the verifier pod.
set -u
cd source || exit 2
PY=/workspace/venv312/bin/python
export PYTHONPATH="$PWD/tools/research/src:$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/backends/sp1/python:$PWD"
$PY -c "import pytest, sys; print('pytest', pytest.__version__, sys.version)" || $PY -m pip install -q pytest
$PY -m pytest -q -p no:cacheprovider backends/numerical/tests/bench 2>&1 | tail -40
echo "bench rc=${PIPESTATUS[0]}"
$PY -m pytest -q -p no:cacheprovider tools/research/tests -k "vocab or label" 2>&1 | tail -20
echo "research rc=${PIPESTATUS[0]}"
