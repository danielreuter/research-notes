#!/usr/bin/env bash
# hash-commit, 4090 fp8-ada l=8192 p4: tests on the tip (b862be30: synthetic sets carry their drawn operand arrays), then
# ${ROUNDS:-3} alternating rounds 0b40ae8a (/workspace/src-0b40ae8a, the previous tip as synced) / tip, CREPS 5.
source /workspace/hash-commit/scripts/lib.sh
grep -q b862be30 /workspace/src/.research-source.json || { echo "src is not b862be30" | tee -a $LOG; exit 1; }
[ -n "$SKIP_TESTS" ] || tests /workspace/src backends/direct/ligero/hashchain_test.py backends/direct/ligero/leaf_test.py
export CREPS=${CREPS:-5}
for R in $(seq ${R0:-5} $(( ${R0:-5} + ${ROUNDS:-3} - 1 ))); do
  run k0b40-fp8ada-l8192-p4-r$R /workspace/src-0b40ae8a fp8-ada 8192 4 5
  run tip-fp8ada-l8192-p4-r$R /workspace/src fp8-ada 8192 4 5
done
