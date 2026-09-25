#!/bin/bash
# GPU spot row #101 (llama32-1b B1 256/32 stoch, l40s): `row_pod.sh build,match,commit` PAIRS=1 (the record's --pairs 1) from the
# head tree, then the base tree, both layout variables unset (a4's row101.sh; trees /workspace/{head,base}; logs in the run dir).
# Record: run root 7adcef49...; base rebuild (f3, a4, c1): program ccc213475e7c4eed, manifest 90f8186879d5035a.
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
L=${RESEARCH_RUN_DIR:-/workspace/c2/r101}; mkdir -p $L
if [ ! -e /workspace/bootstrap/.c2-gpu-ok ]; then
  ( cd /workspace/head/integrations/vllm && MAX_JOBS=32 bash verity_vllm/ops/pod_bootstrap.sh --gpu --cases LLAMA32_1B --out /workspace/bootstrap ) > $L/bootstrap.log 2>&1
  grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK: $(tail -5 $L/bootstrap.log)"; exit 3; }
  touch /workspace/bootstrap/.c2-gpu-ok
fi
echo "bootstrap OK $(date -u +%FT%TZ)"
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
for pair in head:/workspace/head base:/workspace/base; do
  TAG=${pair%%:*}; T=${pair#*:}
  (
    cd "$T/integrations/vllm" || exit 3
    unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
    export SWEEP_DIR=/workspace/cp/sweep-$TAG PAIRS=1
    echo "start $(date -u +%FT%TZ) tree $T ($TAG)"
    env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL|MAX_JOBS)'
    bash verity_vllm/ops/row_pod.sh $ROW LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da build,match,commit
    rc=$?
    echo "exit $rc $(date -u +%FT%TZ)"
    cat "$SWEEP_DIR/$ROW/stages.txt"
  ) > $L/r101_$TAG.log 2>&1
  echo "$TAG: $(grep '^exit' $L/r101_$TAG.log)"
done
/workspace/venv312/bin/python - "$L" <<'PY'
import glob, json, sys
ROW = "llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager"
REC = {"run_roots": ["7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5"], "program": "ccc213475e7c4eed", "manifest": "90f8186879d5035a"}
print("expected", REC)
out = {}
for tag in ("head", "base"):
    d = f"/workspace/cp/sweep-{tag}/{ROW}"
    try:
        v = json.load(open(f"{d}/commit/verdict.json"))
    except Exception as e:
        print(tag, "no verdict:", e); continue
    rm = v.get("required_manifest") or {}
    out[tag] = {"run_roots": v.get("run_roots"), "commit_pass": v.get("commit_pass"), "program_digest": rm.get("program_digest"),
                "manifest_digest": rm.get("manifest_digest"), "first_fail_reason": v.get("first_fail_reason"),
                "checks": {c.get("name", str(i)): c.get("status") for i, c in enumerate(v.get("checks", []))} if isinstance(v.get("checks"), list) else v.get("checks")}
    print(tag, "run_roots", v.get("run_roots"), "== record:", v.get("run_roots") == REC["run_roots"], "| commit_pass", v.get("commit_pass"),
          "| program", rm.get("program_digest"), "manifest", rm.get("manifest_digest"), "| first_fail", v.get("first_fail_reason"))
json.dump(out, open(sys.argv[1] + "/r101_summary.json", "w"), indent=1)
if len(out) == 2:
    print("head == base:", {k: out["head"][k] == out["base"][k] for k in ("run_roots", "commit_pass", "program_digest", "manifest_digest")})
PY
tar -czf $L/r101_outputs.tgz -C /workspace/cp --exclude='*.safetensors' --exclude='*.bin' --exclude='*.pt' \
  $(cd /workspace/cp && ls -d sweep-*/$ROW/{build,match,commit}/*.json sweep-*/$ROW/stages.txt 2>/dev/null) 2>/dev/null
echo "done $(date -u +%FT%TZ)"
