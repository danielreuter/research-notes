#!/usr/bin/env bash
# red-team-standard-hash, 12:15Z: (1) blake3-xob class review at b-ligero-standard-hash 5b28557b (/workspace/src-xob) and
# (2) bf16-hopper-x4+sha256 at main 2c92b9e3 (/workspace/src-m2).  Each tree builds its own ligero-verify into its own
# CARGO_TARGET_DIR (no stale binary).  Chain E (end to end, sequential) and chain S (gadget scans) run side by side.
set -uo pipefail
source /workspace/env.sh
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VY_CPU_THREADS=2
O=/workspace/red-team-standard-hash; mkdir -p $O
build() {  # T
  cd /workspace/src-$1
  CARGO_TARGET_DIR=/workspace/cargo-$1 cargo build --release --manifest-path backends/ligero-verify/Cargo.toml 2>&1 | tail -1
  cp /workspace/cargo-$1/release/ligero-verify /workspace/bin/ligero-verify-$1
  sha256sum /workspace/bin/ligero-verify-$1
}
echo "== build"; build xob; build m2
cmp -s /workspace/bin/ligero-verify-xob /workspace/bin/ligero-verify-m2 && echo "WARNING: xob and m2 binaries identical"
pp() { echo "/workspace/src-$1/packages/verity/src:/workspace/src-$1/backends/numerical/python:/workspace/src-$1/tools/research/src:/workspace/src-$1"; }

chainE() {
  X=$O/xob; rm -rf $X; mkdir -p $X; cp /workspace/src-xob/.research-source.json $X/source.json
  B=/workspace/bin/ligero-verify-xob; cd /workspace/src-xob; export PYTHONPATH=$(pp xob)
  for pair in "blake3 blake3-xob" "blake3-xob blake3"; do set -- $pair
    $PY -m backends.direct.ligero.redteam.rtsh_twin_relabel --bin $B --leaf $1 --twin $2 --out $X/relabel-$1-as-$2 > $X/relabel-$1-as-$2.log 2>&1
    echo "relabel $1 as $2 rc=$?"; tail -1 $X/relabel-$1-as-$2.log | cut -c1-600
  done
  for spec in "fp8-ada 48" "fp8-ada 64" "fp8-ada-x4 12" "fp8-ada-x4 24"; do set -- $spec
    $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation $1 --leaf blake3-xob --steps $2 --out $X/h2-$1-$2 > $X/h2-$1-$2.log 2>&1
    echo "h2 $1 steps $2 rc=$?"; tail -1 $X/h2-$1-$2.log | cut -c1-400
  done
  $PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $B --out $X/r1 --relation fp8-ada --leaf blake3-xob --set-binding > $X/r1.log 2>&1
  echo "r1 rc=$?"; grep -E "^(forgery|control)" $X/r1.log | cut -c1-400
  $PY -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $B --out $X/r4 --relation fp8-ada --leaf blake3-xob --vus 3 > $X/r4.log 2>&1
  echo "r4 rc=$?"; tail -4 $X/r4.log | cut -c1-400

  M=$O/bf16sha; rm -rf $M; mkdir -p $M; cp /workspace/src-m2/.research-source.json $M/source.json
  B=/workspace/bin/ligero-verify-m2; cd /workspace/src-m2; export PYTHONPATH=$(pp m2)
  for s in 24 48; do
    $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation bf16-hopper-x4 --leaf sha256 --steps $s --out $M/h2-$s > $M/h2-$s.log 2>&1
    echo "bf16 h2 steps $s rc=$?"; tail -1 $M/h2-$s.log | cut -c1-400
  done
  $PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $B --out $M/r1 --relation bf16-hopper-x4 --leaf sha256 --set-binding > $M/r1.log 2>&1
  echo "bf16 r1 rc=$?"; grep -E "^(forgery|control)" $M/r1.log | cut -c1-400
  $PY -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $B --out $M/r4 --relation bf16-hopper-x4 --leaf sha256 --vus 3 > $M/r4.log 2>&1
  echo "bf16 r4 rc=$?"; tail -4 $M/r4.log | cut -c1-400
  echo CHAIN-E-DONE
}

chainS() {
  cd /workspace/src-xob; export PYTHONPATH=$(pp xob)
  $PY -m backends.direct.ligero.redteam.rtsh_blake3_free_rows --leaf blake3-xob --shapes 8:0.5,8:2 --control-shape 8:0.5 --out $O/free-xob > $O/free-xob.log 2>&1
  echo "free xob rc=$?"; cut -c1-330 $O/free-xob.log
  cd /workspace/src-m2; export PYTHONPATH=$(pp m2)
  $PY -m backends.direct.ligero.redteam.rtsh_blake3_free_rows --leaf sha256 --shapes 16:2 --control-shape 16:2 --out $O/free-sha16 > $O/free-sha16.log 2>&1
  echo "free sha256 16:2 rc=$?"; cut -c1-330 $O/free-sha16.log
  echo CHAIN-S-DONE
}

chainE > $O/chainE.out 2>&1 &
chainS > $O/chainS.out 2>&1 &
wait
echo SUITE-DONE
