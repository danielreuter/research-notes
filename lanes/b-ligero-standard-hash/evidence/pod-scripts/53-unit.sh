#!/usr/bin/env bash
# b-ligero-standard-hash: reverify/hashauth unit tests on the current tree, then the R4 check (52-r4check.sh) again on it.
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 52-r4check.sh --send 53-unit.sh \
#     --send rtsh_orphan_e2e.py --env DUMP=/workspace/research/runs/r20260925-073210-f45c/sweep/p4-16384/proofs \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/53-unit.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
$PY -m pytest -q backends/direct/ligero/reverify_test.py backends/direct/ligero/hashauth_test.py 2>&1 | tail -n 15
echo "pytest rc=${PIPESTATUS[0]}"
bash "$IN/52-r4check.sh"
