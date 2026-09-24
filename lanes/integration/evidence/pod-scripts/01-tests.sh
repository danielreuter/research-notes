#!/usr/bin/env bash
# integration merge-val-3 (a): cargo test ligero-verify, cargo check backends/direct workspace, full pytest backends/direct/ligero
source /workspace/env.sh
cd /workspace/src
O=/workspace/integration/tests; mkdir -p $O
(
  cd backends/ligero-verify && cargo test --release > $O/cargo_test.log 2>&1; echo "CARGO_TEST_EXIT $?" >> $O/cargo_test.log
  cd /workspace/src/backends/direct && cargo check --workspace > $O/cargo_check_direct.log 2>&1; echo "CARGO_CHECK_EXIT $?" >> $O/cargo_check_direct.log
) &
LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 $PY -m pytest backends/direct/ligero -q -p no:cacheprovider -rfE \
  > $O/pytest.log 2>&1
echo "PYTEST_EXIT $?" >> $O/pytest.log
wait
echo TESTS_DONE >> $O/pytest.log
