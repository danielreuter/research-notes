#!/usr/bin/env bash
# red-team-standard-hash-2, 14:48Z: H100 +blake3 cells (bf16-hopper+blake3, fp8-hopper+blake3) at main 2c92b9e3
# (/workspace/src-m2 = git archive of 2c92b9e3 + redteam overlay 041ac181; ligero-verify-m2 9602aba7, built 12:18Z).
# bf16-hopper: steps 96, k 16 BF16 words = 32 bytes -> blake3 column shape 16:0.5 (not in the 1027Z scan).
# fp8-hopper: steps 48, k 32 E4M3 words -> 8:0.5 (scanned at 1027Z); here only the relation-level attacks.
set -uo pipefail
source /workspace/env.sh
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VY_CPU_THREADS=2
O=/workspace/red-team-standard-hash-2; mkdir -p $O
B=/workspace/bin/ligero-verify-m2; cd /workspace/src-m2
export PYTHONPATH=/workspace/src-m2/packages/verity/src:/workspace/src-m2/backends/numerical/python:/workspace/src-m2/tools/research/src:/workspace/src-m2
cp .research-source.json $O/source.json; sha256sum $B > $O/bin.sha256

chainS() {
  $PY -m backends.direct.ligero.redteam.rtsh_blake3_free_rows --leaf blake3 --shapes 16:0.5 --control-shape 16:0.5 --out $O/free-b3-16h > $O/free-b3-16h.log 2>&1
  echo "free blake3 16:0.5 rc=$?"; cut -c1-330 $O/free-b3-16h.log
  echo CHAIN-S-DONE
}
chainE() {
  for spec in "bf16-hopper 96" "bf16-hopper 128" "fp8-hopper 48" "fp8-hopper 64"; do set -- $spec
    $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation $1 --leaf blake3 --steps $2 --out $O/h2-$1-$2 > $O/h2-$1-$2.log 2>&1
    echo "h2 $1 steps $2 rc=$?"; tail -1 $O/h2-$1-$2.log | cut -c1-400
  done
  for rel in bf16-hopper fp8-hopper; do
    $PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $B --out $O/r1-$rel --relation $rel --leaf blake3 --set-binding > $O/r1-$rel.log 2>&1
    echo "r1 $rel rc=$?"; grep -E "^(forgery|control)" $O/r1-$rel.log | cut -c1-400; tail -1 $O/r1-$rel.log
    $PY -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $B --out $O/r4-$rel --relation $rel --leaf blake3 --vus 3 > $O/r4-$rel.log 2>&1
    echo "r4 $rel rc=$?"; tail -4 $O/r4-$rel.log | cut -c1-400
  done
  echo CHAIN-E-DONE
}
chainS > $O/chainS.out 2>&1 &
chainE > $O/chainE.out 2>&1 &
wait
echo SUITE-DONE
