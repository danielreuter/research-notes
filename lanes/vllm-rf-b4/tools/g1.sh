#!/bin/bash
# 1x L40S: bootstrap (LLAMA32_1B, B0); row #101 `row_pod.sh build,match,commit` PAIRS=1 (the record's --pairs 1; its Commit runs the
# FA2 matReq tap) at head; then properties.noninterference (observer / forward hooks / bare) at head and at base.
#   logs: /workspace/b4/logs/{bootstrap,r101_head,nonint_head,nonint_base}.log
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
L=/workspace/b4/logs; mkdir -p $L
cd /workspace/head/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --gpu --cases LLAMA32_1B,B0 --out /workspace/bootstrap > $L/bootstrap.log 2>&1
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK: $(tail -2 $L/bootstrap.log)"; exit 3; }
echo "bootstrap OK $(date -u +%FT%TZ)"
(
  cd /workspace/head/integrations/vllm || exit 3
  unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
  export SWEEP_DIR=/workspace/cp/sweep-head PAIRS=1
  echo "start $(date -u +%FT%TZ)"
  env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL|VLLM)'
  bash verity_vllm/ops/row_pod.sh $ROW LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da build,match,commit
  echo "exit $? $(date -u +%FT%TZ)"
  cat "$SWEEP_DIR/$ROW/stages.txt"
) > $L/r101_head.log 2>&1
echo "r101 head: $(grep '^exit' $L/r101_head.log)"
/workspace/venv312/bin/python - <<'PY'
import json
ROW = "llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager"
REC = {"run_roots": ["7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5"], "program": "ccc213475e7c4eed", "manifest": "90f8186879d5035a"}
print("expected", REC)
d = f"/workspace/cp/sweep-head/{ROW}"
try:
    v = json.load(open(f"{d}/commit/verdict.json"))
except Exception as e:
    print("head no verdict:", e)
else:
    rm = v.get("required_manifest") or {}
    print("head run_roots", v.get("run_roots"), "== record:", v.get("run_roots") == REC["run_roots"], "| commit_pass", v.get("commit_pass"),
          "| program", rm.get("program_digest"), "manifest", rm.get("manifest_digest"), "| first_fail", v.get("first_fail_reason"))
PY
for pair in head:/workspace/head base:/workspace/base; do
  TAG=${pair%%:*}; T=${pair#*:}
  (
    cd "$T/integrations/vllm" || exit 3
    export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src HF_HOME=/workspace/hf
    unset VLLM_BATCH_INVARIANT VLLM_USE_V2_MODEL_RUNNER VLLM_ENABLE_V1_MULTIPROCESSING VLLM_USE_FLASHINFER_SAMPLER HF_HUB_OFFLINE
    echo "start $(date -u +%FT%TZ) tree $T ($TAG)"
    python -m verity_vllm.properties.noninterference --workload workloads/workload_32x16_1req.json --out /workspace/cp/nonint-$TAG
    echo "exit $? $(date -u +%FT%TZ)"
  ) > $L/nonint_$TAG.log 2>&1
  echo "nonint $TAG: $(grep -E '^\[nonint\] (PASS|FAIL)' $L/nonint_$TAG.log) $(grep '^exit' $L/nonint_$TAG.log)"
done
echo "done $(date -u +%FT%TZ)"
