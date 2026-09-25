#!/usr/bin/env bash
# commit-gpu: the suites next to the change (hashchain row_chain, leaf_test, the core leaf schemas, the core commitments,
# hash_gpu), --durations for the slow ones.  HEAVY=1 adds leaf/{blake3,conformance}_test.py (CPU BLAKE3 gadget builds:
# minutes per test on 12 cores).
source /workspace/hash-commit-2/scripts/lib.sh
extra=""; [ -n "${HEAVY:-}" ] && extra="backends/direct/ligero/leaf/blake3_test.py backends/direct/ligero/leaf/conformance_test.py"
tests /workspace/src --durations=15 backends/shared/hash_gpu/tests backends/direct/ligero/hashchain_test.py backends/direct/ligero/leaf_test.py \
  backends/direct/ligero/leaf/core_schema_test.py packages/verity/tests/commitments $extra
cp $HC/tests.log $HC/tests-neighbours${HEAVY:+-heavy}.log
