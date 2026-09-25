#!/usr/bin/env bash
# red-team-standard-hash: H2 (steps pin) end to end on fp8-hopper-x4+sha256 at b-ligero-sha256 da74b03e (/workspace/src-sha2),
# with the ligero-verify built from that tree by final_suite.sh.  Pinned steps 12; 24 and 6 must be refused.
set -uo pipefail
source /workspace/env.sh
export OMP_NUM_THREADS=$(nproc) MKL_NUM_THREADS=$(nproc) OPENBLAS_NUM_THREADS=$(nproc) VY_CPU_THREADS=$(nproc)
cd /workspace/src-sha2
O=/workspace/red-team-standard-hash/h2-hopper-x4-sha256; rm -rf $O; mkdir -p $O
cat .research-source.json > $O/source.json 2>/dev/null || echo '{"commit": "da74b03e"}' > $O/source.json
B=/workspace/bin/ligero-verify-sha2; sha256sum $B | tee $O/bin.sha256
for s in 12 24 6; do
  $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation fp8-hopper-x4 --leaf sha256 --steps $s --out $O/h2-steps$s > $O/h2-steps$s.log 2>&1
  echo "steps $s rc=$?"; tail -1 $O/h2-steps$s.log | cut -c1-400
done
echo H2-HOPPER-DONE
