#!/usr/bin/env bash
# red-team-standard-hash: re-test R1 / R2 / H2 against lane/b-ligero-standard-hash 806a2f73 (synced to /workspace/src-fix), and R4.
set -uo pipefail
source /workspace/env.sh
export OMP_NUM_THREADS=$(nproc) MKL_NUM_THREADS=$(nproc) OPENBLAS_NUM_THREADS=$(nproc) VY_CPU_THREADS=$(nproc)
cd /workspace/src-bls
O=/workspace/red-team-standard-hash/bls-806a2f73; rm -rf $O; mkdir -p $O
cat .research-source.json > $O/source.json
echo "=== build"; cargo build --release --manifest-path backends/ligero-verify/Cargo.toml 2>&1 | tail -2
cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ligero-verify-bls; B=/workspace/bin/ligero-verify-bls; sha256sum $B | tee $O/bin.sha256
echo "=== R1 remap (expect NOT reproduced)"
$PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $B --out $O/r1 --set-binding > $O/r1.log 2>&1; echo "r1 rc=$?"; grep -E "^(forgery|control)" $O/r1.log | cut -c1-300
echo "=== R4 orphan"
$PY -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $B --out $O/r4 --vus 3 > $O/r4.log 2>&1; echo "r4 rc=$?"; tail -5 $O/r4.log | cut -c1-400
echo "=== R4 vs verify-night-2 06"
VN2_N=3 VY_CPU_THREADS=4 $PY $RESEARCH_RUN_DIR/inputs/vn2_check_on_r1.py $O/r4 $RESEARCH_RUN_DIR/inputs/vn2-06b.py control orphan-stmt stmt-entry > $O/r4-vn2.log 2>&1; echo "vn2 rc=$?"
grep -E "^(control|orphan-stmt|stmt-entry):|^\{\"" $O/r4-vn2.log | cut -c1-300
echo "=== H2 on the fix"
for s in 48 64; do
  $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation fp8-ada --leaf blake3 --steps $s --out $O/h2-steps$s > $O/h2-steps$s.log 2>&1; echo "steps $s rc=$?"; tail -2 $O/h2-steps$s.log | cut -c1-300
done
