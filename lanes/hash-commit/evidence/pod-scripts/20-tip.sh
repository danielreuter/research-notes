#!/usr/bin/env bash
# hash-commit, 4090 fp8-ada l=8192 p4: the committer's tests, then the AFTER committer (tree /workspace/src = lane/hash-commit
# tip, the row_sponge kernel) with the same bench as 10-base.sh.
source /workspace/hash-commit/scripts/lib.sh
[ -n "$SKIP_TESTS" ] || tests /workspace/src backends/direct/ligero/hashchain_test.py -k "row_sponge or sponge_kernel or precomputed or committer"
run tip-fp8ada-l8192-p4-r${R:-1} /workspace/src fp8-ada 8192 4 5
