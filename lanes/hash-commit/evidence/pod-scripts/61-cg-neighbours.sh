#!/usr/bin/env bash
# commit-gpu: the suites next to the change (hashchain row_chain, the leaf schemes' conformance incl. BLAKE3, the core
# commitments, hash_gpu); the ajtai leaf tests (untouched) excluded; --durations for the slow ones.
source /workspace/hash-commit/scripts/lib.sh
tests /workspace/src --durations=15 backends/shared/hash_gpu/tests backends/direct/ligero/hashchain_test.py backends/direct/ligero/leaf_test.py \
  backends/direct/ligero/leaf/blake3_test.py backends/direct/ligero/leaf/conformance_test.py backends/direct/ligero/leaf/core_schema_test.py \
  packages/verity/tests/commitments
cp $HC/tests.log $HC/tests-neighbours.log
