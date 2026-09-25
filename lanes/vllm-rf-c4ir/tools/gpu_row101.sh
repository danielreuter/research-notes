#!/bin/bash
# GPU smoke, one research run from the shipped head tree ($PWD): frozen row #101 (llama32-1b B1 256/32 stoch, l40s)
# `row_pod.sh build,match,commit` PAIRS=1 (the record's --pairs 1), layout variables unset (a4's tools/row101.sh, head only).
# Record: run root 7adcef49..., program ccc213475e7c4eed..., manifest 90f8186879d5035a...
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
S=$PWD; L=$RESEARCH_RUN_DIR; H=/workspace/c4ir-head
unset PYTHONPATH
echo "start $(date -u +%FT%TZ) src $S"
rm -rf $H && cp -a $S $H && find $H -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
(cd $H/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --gpu --cases LLAMA32_1B --out /workspace/bootstrap) > $L/bootstrap.log 2>&1
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK: $(tail -2 $L/bootstrap.log)"; exit 3; }
echo "bootstrap OK $(date -u +%FT%TZ)"
PATH=$HOME/.local/bin:$PATH uv pip freeze --python /workspace/venv312/bin/python > $L/freeze.txt 2>&1
export SWEEP_DIR=/workspace/cp/sweep-head PAIRS=1
D=$SWEEP_DIR/$ROW
(
  cd $H/integrations/vllm || exit 3
  unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT PYTHONPATH
  echo "start $(date -u +%FT%TZ) tree $H"
  env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL)'
  bash verity_vllm/ops/row_pod.sh $ROW LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da build,match,commit
  rc=$?
  echo "exit $rc $(date -u +%FT%TZ)"
  cat "$D/stages.txt"
) > $L/r101_head.log 2>&1
echo "head: $(grep '^exit' $L/r101_head.log)"
mkdir -p $L/sweep && (cd $D && find . \( -name '*.json' -o -name '*.txt' -o -name '*.md' \) -size -5M -exec cp --parents {} $L/sweep/ \;)
/workspace/venv312/bin/python - "$D" <<'PY' | tee $L/r101_compare.txt
import json, sys
d = sys.argv[1]
REC = {"run_roots": ["7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5"],
       "program": "ccc213475e7c4eed04b3b0d3717e2144012be65f41d900a018dbd09d1e400c6b",
       "manifest": "90f8186879d5035af027259151b4ac465bf6c3dcf08c1e6d62dab9b680bfeaac"}
print("expected", REC)
try:
    v = json.load(open(f"{d}/commit/verdict.json"))
except Exception as e:
    print("head no verdict:", e); sys.exit(0)
rm = v.get("required_manifest") or {}
print("head run_roots", v.get("run_roots"), "== record:", v.get("run_roots") == REC["run_roots"])
print("head program", rm.get("program_digest"), "== record:", rm.get("program_digest") == REC["program"])
print("head manifest", rm.get("manifest_digest"), "== record:", rm.get("manifest_digest") == REC["manifest"])
print("head commit_pass", v.get("commit_pass"), "| first_fail", v.get("first_fail_reason"))
PY
echo "done $(date -u +%FT%TZ)"
