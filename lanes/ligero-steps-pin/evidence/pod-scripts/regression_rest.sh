#!/usr/bin/env bash
# ligero-steps-pin: the regression tests after position 134 of /workspace/lsp/collect.txt (the first run was stopped on
# conformance_test::test_committed_operand_negatives_rejected[blake3], > 40 min on this CPU pod), minus the conformance
# suite's [blake3] cases (the blake3 gadget proves too slowly on CPU; blake3 is covered by blake3_test.py in the first
# run and the three R2 +blake3 fixtures in the reverify run).
set -uo pipefail
source /workspace/env.sh
cd /workspace/src
sed -n '135,188p' /workspace/lsp/collect.txt | grep '::' | grep -v 'conformance_test.py::.*\[blake3\]' > /workspace/lsp/rest.txt
wc -l < /workspace/lsp/rest.txt
$PY -m pytest -p no:cacheprovider -q -rfEs --timeout 1800 $(cat /workspace/lsp/rest.txt) 2>&1 | tee /workspace/lsp/pytest_regression_rest.log | tail -25
