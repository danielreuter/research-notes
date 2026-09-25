#!/usr/bin/env bash
# red-team-standard-hash-2, 14:58Z: extra H2 forgeries for bf16-hopper+blake3 (steps 128 hit the gadget's 2..3-chunk
# refusal before any verifier ran, so it tested nothing). Same tree and binary as hopper_blake3_suite.sh.
set -uo pipefail
source /workspace/env.sh
export OMP_NUM_THREADS=1 VY_CPU_THREADS=1
O=/workspace/red-team-standard-hash-2; B=/workspace/bin/ligero-verify-m2; cd /workspace/src-m2
export PYTHONPATH=/workspace/src-m2/packages/verity/src:/workspace/src-m2/backends/numerical/python:/workspace/src-m2/tools/research/src:/workspace/src-m2
for s in 48 192; do
  $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation bf16-hopper --leaf blake3 --steps $s --out $O/h2-bf16-hopper-$s > $O/h2-bf16-hopper-$s.log 2>&1
  echo "h2 bf16-hopper steps $s rc=$?"; tail -1 $O/h2-bf16-hopper-$s.log | cut -c1-400
done
echo SUITE2B-DONE
