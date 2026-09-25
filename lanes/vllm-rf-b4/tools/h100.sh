#!/bin/bash
# 1x H100 (cc 9.0, FlashAttention-3 engine): bootstrap (LLAMA32_1B; builds the FA3 matReq tap), then the Llama-3.2-1B B1 1024/128 H100
# row `row_pod.sh build,match,commit` PAIRS=1 from the head tree and from the base tree (its Commit runs the FA3 tap), and the head vs
# base comparison: run root, verdict, Program / manifest digests, hidden class; plus the cc 9.0 known root of verity_vllm/ops/known_roots.json.
#   needs: /workspace/head (head tree), /workspace/b4/base.diff (git diff --binary BASE HEAD)
#   logs: /workspace/b4/logs/{bootstrap,h100_head,h100_base}.log   rows: /workspace/cp/sweep-{head,base}/<row>/
ROW=llama32-1b__bf16__h100__tp1__b1__i1024__o128__mixed__greedy__bi-eager
L=/workspace/b4/logs; mkdir -p $L
if [ ! -d /workspace/base/integrations/vllm ]; then
  cp -a /workspace/head /workspace/base && (cd /workspace/base && git apply -R /workspace/b4/base.diff) || { echo "base tree: git apply -R failed"; exit 3; }
fi
test -e /workspace/base/integrations/vllm/verity_vllm/engine/hooks.py && { echo "base tree still has engine/hooks.py"; exit 3; }
cd /workspace/head/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --gpu --cases LLAMA32_1B --out /workspace/bootstrap > $L/bootstrap.log 2>&1
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK: $(tail -2 $L/bootstrap.log)"; exit 3; }
echo "bootstrap OK $(date -u +%FT%TZ) $(grep -o 'FA3-TAP-OK.*' $L/bootstrap.log | tail -1)"
for pair in head:/workspace/head base:/workspace/base; do
  TAG=${pair%%:*}; T=${pair#*:}
  (
    cd "$T/integrations/vllm" || exit 3
    unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
    export SWEEP_DIR=/workspace/cp/sweep-$TAG PAIRS=1
    echo "start $(date -u +%FT%TZ) tree $T ($TAG)"
    env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL|VLLM)'
    bash verity_vllm/ops/row_pod.sh $ROW LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da build,match,commit
    echo "exit $? $(date -u +%FT%TZ)"
    cat "$SWEEP_DIR/$ROW/stages.txt"
  ) > $L/h100_$TAG.log 2>&1
  echo "h100 $TAG: $(grep '^exit' $L/h100_$TAG.log)"
done
/workspace/venv312/bin/python - <<'PY'
import json
ROW = "llama32-1b__bf16__h100__tp1__b1__i1024__o128__mixed__greedy__bi-eager"
known = json.load(open("/workspace/head/integrations/vllm/verity_vllm/ops/known_roots.json"))["roots"].get(ROW, {}).get("9.0")
print("known root cc 9.0:", known)
got = {}
for tag in ("head", "base"):
    try:
        got[tag] = json.load(open(f"/workspace/cp/sweep-{tag}/{ROW}/commit/verdict.json"))
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
    print("head == known:", (h.get("run_roots") or [None])[0] == known)
PY
echo "done $(date -u +%FT%TZ)"
