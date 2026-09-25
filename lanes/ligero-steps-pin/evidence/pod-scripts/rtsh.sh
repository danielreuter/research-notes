#!/usr/bin/env bash
# ligero-steps-pin: red-team-standard-hash's harnesses (lane/red-team-standard-hash 21393756, copied to /workspace/rt) on
# this tree + the new binary.  remap (R1) and orphan (R4) exit 0 when the attack reproduces -> must exit 1 here; steps (H2)
# exits 0 when both verifiers behave as expected for that steps value.  Then hashauth_test + reverify_test at this tip.
set -uo pipefail
source /workspace/env.sh
cd /workspace/src
O=/workspace/lsp/rtsh; mkdir -p $O; rc=0
cp /workspace/rt/rtsh_*.py backends/direct/ligero/redteam/
run() { local want=$1 tag=$2; shift 2; echo "=== $(date -u +%H:%M:%SZ) $tag (want exit $want)"
  $PY -m backends.direct.ligero.redteam.$@ 2>&1 | tee $O/$tag.log | tail -6; local e=${PIPESTATUS[0]}
  echo "--- $tag exit $e (want $want)"; [ $e -eq $want ] || rc=1; }
run 1 remap rtsh_remap_e2e --bin $LIGERO_VERIFY --out $O/remap --set-binding
run 1 orphan rtsh_orphan_e2e --bin $LIGERO_VERIFY --out $O/orphan --vus 3
for s in 48 32 64; do run 0 steps$s rtsh_steps_e2e --bin $LIGERO_VERIFY --leaf blake3 --steps $s --out $O/steps$s; done
echo "=== $(date -u +%H:%M:%SZ) pytest hashauth_test reverify_test"
$PY -m pytest -p no:cacheprovider -q -rfEs --timeout 3600 backends/direct/ligero/hashauth_test.py backends/direct/ligero/reverify_test.py \
  2>&1 | tee $O/pytest_r4.log | tail -12
[ ${PIPESTATUS[0]} -eq 0 ] || rc=1
echo "=== $(date -u +%H:%M:%SZ) done rc=$rc"; exit $rc
