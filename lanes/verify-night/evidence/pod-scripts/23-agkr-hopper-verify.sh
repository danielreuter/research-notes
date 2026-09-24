#!/usr/bin/env bash
# verify-night: A-GKR H100 BF16 (bf16-hopper) bench-result (agkr-table handoff 20260924T0830Z).
#   TREE=art:<run-files> TAG=<name> bash 23-agkr-hopper-verify.sh     (AWS_* read credential in the environment)
# Verifier: /workspace/agkr-target/release/verity-gkr-verify (53bd441b; `git diff 53bd441b 5b3a4646 -- backends/gkr/verifier` empty).
# Statement: 22-agkr-hopper-statement.py (my tree, hopper_bf16_m16n8k16 Params; public.bin vs my frozen bf16-hopper y).
# Negatives: `mutate --sample 64` on rep0 (new circuit and proof bytes: every mutation must be rejected).
set -uo pipefail
source /workspace/env.sh
V=/workspace/agkr-target/release/verity-gkr-verify
O=/workspace/verify-night/agkr-$TAG; mkdir -p $O
{
sha256sum $V
echo "=== [$(date -u +%H:%M:%S)] fetch $TREE"
[ -d $O/tree ] || $PY -m research data fetch $TREE --to $O/tree | tail -1
D=$(dirname $(find $O/tree -name public.bin | head -1))/..; D=$(cd $D && pwd); echo "tree: $D"
sha256sum $D/proofs/*.bin $D/statement/*
echo "=== [$(date -u +%H:%M:%S)] statement vs my tree"
(cd /workspace/src/backends/gkr && PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH $PY /workspace/verify-night/22-agkr-hopper-statement.py \
   $D/statement $O/regen | grep -E '"(identical|ok|equals_frozen_y_bf16|equals_frozen_y_fp32|manifest_params_differ|y_bf16_sha256_u16|frozen_relation)"')
echo "=== [$(date -u +%H:%M:%S)] verify"
for r in $D/proofs/rep*.bin; do
  b=$(basename $r .bin)
  $V verify --dir $D/statement --proof $r --vus 4096 --threads 15 --json $O/out_$b.json > $O/verify_$b.log 2>&1; rc=$?
  echo "$b rc=$rc $(head -c 300 $O/out_$b.json 2>/dev/null)"
done
echo "=== [$(date -u +%H:%M:%S)] negatives (mutate --sample 64 on rep0)"
$V mutate --dir $D/statement --proof $D/proofs/rep0.bin --vus 4096 --threads 15 --sample 64 > $O/mutate.log 2>&1; echo "mutate rc=$?"
tail -2 $O/mutate.log
echo "=== [$(date -u +%H:%M:%S)] done"
} >> $O/verify.out 2>&1
