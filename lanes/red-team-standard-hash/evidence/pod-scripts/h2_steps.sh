#!/usr/bin/env bash
# red-team-standard-hash H2 on +LEAF (default blake3): canonical-steps control + forged steps, Rust pinned + Python verify_files.
set -uo pipefail
source /workspace/env.sh
export OMP_NUM_THREADS=$(nproc) MKL_NUM_THREADS=$(nproc) OPENBLAS_NUM_THREADS=$(nproc) VY_CPU_THREADS=$(nproc)
cd /workspace/src
REL=${REL:-fp8-ada}; LEAF=${LEAF:-blake3}; STEPS=${STEPS:-"96 32 48 192"}
O=/workspace/red-team-standard-hash/h2-$REL-$LEAF; mkdir -p $O
fail=0
for s in $STEPS; do
  echo "== steps $s"
  $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin /workspace/bin/ligero-verify --relation $REL --leaf $LEAF --steps $s \
    --out $O/steps$s > $O/steps$s.log 2>&1 || fail=1
  tail -2 $O/steps$s.log
done
exit $fail
