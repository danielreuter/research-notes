#!/bin/bash
# 1x H100 PCIe (cc 9.0, 114 SMs; FlashAttention-3 engine), after h100.sh's bootstrap: the release canary's Llama-3.2-1B B1 256/32
# greedy row `row_pod.sh build,match,commit` PAIRS=1 from the head tree and from the base tree, its Commit with the FA3 matReq tap
# (row_pod.sh picks fa3_matReq on cc 9.0).  The row declares no TargetProfile, so it runs on this part; the target-family precheck
# is waived by name as canary.sh does on the Hopper canary host.  (The H100 rows of record declare 132 SMs, an H100 SXM.)
# Head vs base: run root, verdict, Program / manifest digests, hidden class.
#   logs: /workspace/b4/logs/h100c_{head,base}.log   rows: /workspace/cp/sweep-c-{head,base}/<row>/
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager
L=/workspace/b4/logs; mkdir -p $L
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK"; exit 3; }
for pair in head:/workspace/head base:/workspace/base; do
  TAG=${pair%%:*}; T=${pair#*:}
  (
    cd "$T/integrations/vllm" || exit 3
    unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
    export SWEEP_DIR=/workspace/cp/sweep-c-$TAG PAIRS=1 TARGET_FAMILY_WAIVER="fa3 tap head-vs-base on an H100 PCIe"
    echo "start $(date -u +%FT%TZ) tree $T ($TAG)"
    env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL|VLLM|TARGET)'
    bash verity_vllm/ops/row_pod.sh $ROW LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da build,match,commit
    echo "exit $? $(date -u +%FT%TZ)"
    cat "$SWEEP_DIR/$ROW/stages.txt"
  ) > $L/h100c_$TAG.log 2>&1
  echo "h100c $TAG: $(grep '^exit' $L/h100c_$TAG.log)"
done
/workspace/venv312/bin/python - <<'PY'
import json
ROW = "llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager"
got = {}
for tag in ("head", "base"):
    try:
        got[tag] = json.load(open(f"/workspace/cp/sweep-c-{tag}/{ROW}/commit/verdict.json"))
    except Exception as e:
        print(tag, "no verdict:", e)
for tag, v in got.items():
    rm = v.get("required_manifest") or {}
    fams = sorted({f for c in rm.get("coverage") or [] for f in (c.get("checked_by_family") or {})})
    print(tag, "run_roots", v.get("run_roots"), "| commit_pass", v.get("commit_pass"), "| first_fail", v.get("first_fail_reason"),
          "| program", rm.get("program_digest"), "manifest", rm.get("manifest_digest"), "| families", fams)
if len(got) == 2:
    h, b = got["head"], got["base"]
    hm, bm = (x.get("required_manifest") or {} for x in (h, b))
    print("head == base: run_roots", h.get("run_roots") == b.get("run_roots"), "commit_pass", h.get("commit_pass") == b.get("commit_pass"),
          "program", hm.get("program_digest") == bm.get("program_digest"), "manifest", hm.get("manifest_digest") == bm.get("manifest_digest"))
PY
echo "done $(date -u +%FT%TZ)"
