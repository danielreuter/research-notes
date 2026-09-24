#!/bin/bash
cd /workspace
exec /workspace/run.sh /workspace/src-base tests_pytest_final2 /workspace/venv312/bin/python -m pytest -q -rfE -p no:cacheprovider --durations=12 backends/direct/ligero --deselect backends/direct/ligero/v2 --deselect backends/direct/ligero/fold_test.py::test_folded_unit_is_exactly_four_chained_base_steps --deselect backends/direct/ligero/fold_test.py::test_folded_chain_is_the_base_claim_cpu
