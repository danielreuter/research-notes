#!/usr/bin/env bash
# verify-night: independent verification of an A-GKR bench-result (agkr-table handoffs 20260924T0644Z, 0712Z).
#   TREE=art:<run-files> TAG=<name> [BUILD=1] [MUTATE=1] bash 10-agkr-verify.sh     (AWS_* read credential in the environment)
# Verifier: backends/gkr/verifier (verity-gkr-verify, no dependencies) from lane/agkr-table @ 53bd441b, shipped as
#   `git archive 53bd441b backends/gkr/verifier` to /workspace/agkr, built + tested here (BUILD=1).
# Statement: 11-agkr-statement.py (circuit/epilogue/chain regenerated from MY tree and compared byte-for-byte; public.bin vs
#   the frozen vu-k1536 y of my tree's fixture). MUTATE=1: `mutate --sample 64` on rep0 (all mutations must be rejected).
set -uo pipefail
source /workspace/env.sh
export PATH=$HOME/.cargo/bin:$PATH CARGO_TARGET_DIR=/workspace/agkr-target
V=$CARGO_TARGET_DIR/release/verity-gkr-verify
O=/workspace/verify-night/agkr-$TAG; mkdir -p $O
{
if [ "${BUILD:-0}" = 1 ]; then
  echo "=== [$(date -u +%H:%M:%S)] build"
  (cd /workspace/agkr/backends/gkr/verifier && cargo build --release 2>&1 | tail -2 && cargo test --release 2>&1 | grep -E '^test result|FAILED|panicked' )
fi
sha256sum $V
echo "=== [$(date -u +%H:%M:%S)] fetch $TREE"
[ -d $O/tree ] || $PY -m research data fetch $TREE --to $O/tree | tail -1
D=$(dirname $(find $O/tree -name public.bin | head -1))/..; D=$(cd $D && pwd); echo "tree: $D"
sha256sum $D/proofs/*.bin $D/statement/*
echo "=== [$(date -u +%H:%M:%S)] statement vs my tree"
(cd /workspace/src/backends/gkr && PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH $PY /workspace/verify-night/11-agkr-statement.py \
   $D/statement $O/regen | grep -E '"(identical|ok|equals_frozen_y|manifest_params_differ|dump_manifest_root_is_frozen)"')
echo "=== [$(date -u +%H:%M:%S)] verify"
for r in $D/proofs/rep*.bin; do
  b=$(basename $r .bin)
  $V verify --dir $D/statement --proof $r --vus 4096 --threads 15 --json $O/out_$b.json > $O/verify_$b.log 2>&1; rc=$?
  echo "$b rc=$rc $(head -c 300 $O/out_$b.json 2>/dev/null)"
done
if [ "${MUTATE:-0}" = 1 ]; then
  echo "=== [$(date -u +%H:%M:%S)] negatives (mutate --sample 64 on rep0)"
  $V mutate --dir $D/statement --proof $D/proofs/rep0.bin --vus 4096 --threads 15 --sample 64 > $O/mutate.log 2>&1; echo "mutate rc=$?"
  tail -2 $O/mutate.log
fi
echo "=== [$(date -u +%H:%M:%S)] done"
} >> $O/verify.out 2>&1
