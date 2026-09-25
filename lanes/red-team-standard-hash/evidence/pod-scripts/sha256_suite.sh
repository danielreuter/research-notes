#!/usr/bin/env bash
# red-team-standard-hash: R1 remap, R4 orphan, H2 steps on fp8-ada-x4+sha256 (sha256/row/v1), at b-ligero-sha256 be1a3bcb
# (/workspace/src-sha) and at be1a3bcb + ligero-steps-pin c8a16e2b merged locally (/workspace/src-shafix).
set -uo pipefail
source /workspace/env.sh
export OMP_NUM_THREADS=$(nproc) MKL_NUM_THREADS=$(nproc) OPENBLAS_NUM_THREADS=$(nproc) VY_CPU_THREADS=$(nproc)
for T in sha shafix; do
  cd /workspace/src-$T
  O=/workspace/red-team-standard-hash/$T; rm -rf $O; mkdir -p $O
  cat .research-source.json > $O/source.json
  echo "===== $T build"; cargo build --release --manifest-path backends/ligero-verify/Cargo.toml 2>&1 | tail -1
  cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ligero-verify-$T; B=/workspace/bin/ligero-verify-$T; sha256sum $B | tee $O/bin.sha256
  echo "=== $T R1 remap"
  $PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $B --out $O/r1 --relation fp8-ada-x4 --leaf sha256 --set-binding > $O/r1.log 2>&1; echo "r1 rc=$?"; grep -E "^(forgery|control)|REPRODUCED|not reproduced|Error|error" $O/r1.log | cut -c1-400 | tail -6
  echo "=== $T R4 orphan"
  $PY -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $B --out $O/r4 --relation fp8-ada-x4 --leaf sha256 --vus 3 > $O/r4.log 2>&1; echo "r4 rc=$?"; tail -5 $O/r4.log | cut -c1-400
  echo "=== $T H2"
  for s in 12 24; do
    $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation fp8-ada-x4 --leaf sha256 --steps $s --out $O/h2-steps$s > $O/h2-steps$s.log 2>&1; echo "steps $s rc=$?"; tail -1 $O/h2-steps$s.log | cut -c1-400
  done
done
