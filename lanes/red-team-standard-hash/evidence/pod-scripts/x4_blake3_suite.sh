#!/usr/bin/env bash
# red-team-standard-hash: R1 / R4 / H2 end to end on fp8-ada-x4+blake3 at main 3301c435 (/workspace/src-main), with the
# ligero-verify built from that tree by final_suite.sh.  Pinned steps 12; 24 must be refused.
set -uo pipefail
source /workspace/env.sh
export OMP_NUM_THREADS=$(nproc) MKL_NUM_THREADS=$(nproc) OPENBLAS_NUM_THREADS=$(nproc) VY_CPU_THREADS=$(nproc)
cd /workspace/src-main
O=/workspace/red-team-standard-hash/x4-blake3-main; rm -rf $O; mkdir -p $O
cat .research-source.json > $O/source.json
B=/workspace/bin/ligero-verify-main; sha256sum $B | tee $O/bin.sha256
REL=fp8-ada-x4; LEAF=blake3
for s in 12 24; do
  $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation $REL --leaf $LEAF --steps $s --out $O/h2-steps$s > $O/h2-steps$s.log 2>&1
  echo "steps $s rc=$?"; tail -1 $O/h2-steps$s.log | cut -c1-400
done
echo "=== R1 remap"
$PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $B --out $O/r1 --relation $REL --leaf $LEAF --set-binding > $O/r1.log 2>&1; echo "r1 rc=$?"; grep -E "^(forgery|control)" $O/r1.log | cut -c1-400
echo "=== R4 orphan"
$PY -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $B --out $O/r4 --relation $REL --leaf $LEAF --vus 3 > $O/r4.log 2>&1; echo "r4 rc=$?"; tail -4 $O/r4.log | cut -c1-400
echo X4-BLAKE3-DONE
