#!/usr/bin/env bash
# integration merge-val-3 (b, H1/H2): steps-pin must-rejects through the merged Rust CLI, pinned (default).
# Fresh forges from the merged prover (steps 32 instead of the canonical 48); the committed red-team fixtures
# (fixtures/steps-pin/, no system.bin beside them) are covered by cargo test steps_pin_*.
source /workspace/env.sh
cd /workspace/src
O=/workspace/integration/negatives; rm -rf $O; mkdir -p $O
chk() {  # tag, system, dir
  local tag=$1 sys=$2 d=$3
  $LIGERO_VERIFY verify --system $sys --statement $d/sub_00.stmt --proof $d/sub_00.proof --json $O/$tag.verdict.json > $O/$tag.out 2>&1
  local rc=$?
  local acc=$($PY -c 'import json,sys;x=json.load(open(sys.argv[1]));print(x.get("accepted"), "|", str(x.get("reason") or x.get("error"))[:140])' $O/$tag.verdict.json 2>/dev/null || tail -c 200 $O/$tag.out | tr '\n' ' ')
  echo "$tag rc=$rc accepted=$acc" | tee -a $O/summary.txt
}
for spec in "bare::" "poseidon2:--leaf poseidon2" "ajtai-n64:--leaf ajtai-n64"; do
  tag=${spec%%:*}; args=${spec#*:}; args=${args#:}
  $PY -m backends.direct.ligero.redteam.steps_pin_forge --relation fp8-ada $args --steps 32 --out $O/forge-$tag > $O/forge-$tag.log 2>&1
  echo "forge-$tag rc=$? $(tr -d '\n ' < $O/forge-$tag/forge.json 2>/dev/null | grep -o '"same_system":[a-z]*,"patched_prover_self_verify":\[[a-z]*')" | tee -a $O/summary.txt
  [ -f $O/forge-$tag/system.bin ] && chk forge-$tag-steps32 $O/forge-$tag/system.bin $O/forge-$tag
done
echo NEG_DONE | tee -a $O/summary.txt
