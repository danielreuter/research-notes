#!/bin/bash
# GPU smoke: frozen row #101 (llama32-1b B1 256/32 stoch, l40s) `row_pod.sh build,match,commit` PAIRS=1 (the record's --pairs 1)
# from the head tree, then the base tree (origin/main 00ffe398), both layout variables unset. Record: run root 7adcef49...;
# base rebuild (f3): program ccc213475e7c4eed, manifest 90f8186879d5035a.   logs: /workspace/a4/logs/r101_{head,base}.log, row101.out
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
L=/workspace/a4/logs; mkdir -p $L
cd /workspace/head2/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --gpu --cases LLAMA32_1B --out /workspace/bootstrap > $L/bootstrap.log 2>&1
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK: $(tail -2 $L/bootstrap.log)"; exit 3; }
echo "bootstrap OK $(date -u +%FT%TZ)"
for pair in head:/workspace/head2 base:/workspace/basemain; do
  TAG=${pair%%:*}; T=${pair#*:}
  (
    cd "$T/integrations/vllm" || exit 3
    unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
    export SWEEP_DIR=/workspace/cp/sweep-$TAG PAIRS=1
    echo "start $(date -u +%FT%TZ) tree $T ($TAG)"
    env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL)'
    bash verity_vllm/ops/row_pod.sh $ROW LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da build,match,commit
    rc=$?
    echo "exit $rc $(date -u +%FT%TZ)"
    cat "$SWEEP_DIR/$ROW/stages.txt"
  ) > $L/r101_$TAG.log 2>&1
  echo "$TAG: $(grep '^exit' $L/r101_$TAG.log)"
done
/workspace/venv312/bin/python - <<'PY'
import json
ROW = "llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager"
REC = {"run_roots": ["7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5"], "program": "ccc213475e7c4eed", "manifest": "90f8186879d5035a"}
print("expected", REC)
for tag in ("head", "base"):
    d = f"/workspace/cp/sweep-{tag}/{ROW}"
    try:
        v = json.load(open(f"{d}/commit/verdict.json"))
    except Exception as e:
        print(tag, "no verdict:", e); continue
    rm = v.get("required_manifest") or {}
    print(tag, "run_roots", v.get("run_roots"), "== record:", v.get("run_roots") == REC["run_roots"], "| commit_pass", v.get("commit_pass"),
          "| program", rm.get("program_digest"), "manifest", rm.get("manifest_digest"), "| first_fail", v.get("first_fail_reason"))
PY
echo "done $(date -u +%FT%TZ)"
