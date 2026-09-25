#!/bin/bash
# 1x L40S: row #101 `row_pod.sh build,match,commit` PAIRS=1 from the base tree (g1.sh ran it from head), then the head vs base vs
# record comparison: run root and verdict vs the record's commit/verdict.json, Program / manifest digests head vs base (the record's
# 079ee0a8... / 368283ad... predate the relayout, so no from-scratch Build gives them).
#   logs: /workspace/b4/logs/r101_base.log   rows: /workspace/cp/sweep-{head,base}/<row>/
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
L=/workspace/b4/logs; mkdir -p $L
(
  cd /workspace/base/integrations/vllm || exit 3
  unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
  export SWEEP_DIR=/workspace/cp/sweep-base PAIRS=1
  echo "start $(date -u +%FT%TZ) tree /workspace/base"
  env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL|VLLM)'
  bash verity_vllm/ops/row_pod.sh $ROW LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da build,match,commit
  echo "exit $? $(date -u +%FT%TZ)"
  cat "$SWEEP_DIR/$ROW/stages.txt"
) > $L/r101_base.log 2>&1
echo "r101 base: $(grep '^exit' $L/r101_base.log)"
/workspace/venv312/bin/python - <<'PY'
import json
ROW = "llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager"
REC = "/workspace/research/store/objects/sha256/50182eda8b3a230854a217409db1139f62697dd895c019926716b54398dc5fed"
rec = json.load(open(REC))
got = {}
for tag in ("head", "base"):
    try:
        got[tag] = json.load(open(f"/workspace/cp/sweep-{tag}/{ROW}/commit/verdict.json"))
    except Exception as e:
        print(tag, "no verdict:", e)
for tag, v in [("record", rec), *got.items()]:
    rm = v.get("required_manifest") or {}
    print(tag, "run_roots", v.get("run_roots"), "| commit_pass", v.get("commit_pass"), "| first_fail", v.get("first_fail_reason"),
          "| program", rm.get("program_digest"), "manifest", rm.get("manifest_digest"))
for tag, v in got.items():
    print(tag, "run_roots == record:", v.get("run_roots") == rec.get("run_roots"), "| commit_pass == record:", v.get("commit_pass") == rec.get("commit_pass"))
if len(got) == 2:
    h, b = ((got[t].get("required_manifest") or {}) for t in ("head", "base"))
    print("head == base: program", h.get("program_digest") == b.get("program_digest"), "manifest", h.get("manifest_digest") == b.get("manifest_digest"))
PY
echo "done $(date -u +%FT%TZ)"
