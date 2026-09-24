#!/bin/bash
# D3 acceptance on a FROZEN regression row: #101 llama32-1b B1 256/32 stoch (l40s), `row_pod.sh build,match,commit` PAIRS=1 (as its
# record: --pairs 1), from the head tree then the base tree, VERITY_(LEAF_)LAYOUT unset.  Compares run roots / Program / manifest digests
# with #101's record (commit/verdict.json of art:a4ea1a18...: run root 7adcef49..., program 079ee0a8..., manifest 368283ad...).
#   usage: row101.sh      logs: /workspace/rff3/logs/r101_{head,base}.log   rows: /workspace/cp/sweep-{head,base}/<row>/   summary: logs/row101.out
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
L=/workspace/rff3/logs; mkdir -p $L
while pgrep -f pod_bootstrap.sh >/dev/null; do sleep 20; done
grep -q '^BOOTSTRAP-OK' /workspace/rff3/bootstrap.log || { echo "bootstrap not OK: $(tail -2 /workspace/rff3/bootstrap.log)"; exit 3; }
echo "bootstrap OK $(date -u +%FT%TZ)"
for pair in head:/workspace/head base:/workspace/basetree; do
  TAG=${pair%%:*}; T=${pair#*:}
  [ -d "$T/integrations/vllm" ] || { echo "$TAG: no tree at $T"; continue; }
  (
    cd "$T/integrations/vllm" || exit 3
    unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
    export SWEEP_DIR=/workspace/cp/sweep-$TAG PAIRS=1
    echo "start $(date -u +%FT%TZ) tree $T $(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["commit"])' $T/.research-source.json)"
    env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL)'
    bash verity_vllm/ops/row_pod.sh $ROW LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da build,match,commit
    rc=$?
    echo "exit $rc $(date -u +%FT%TZ)"
    cat "$SWEEP_DIR/$ROW/stages.txt"
  ) > $L/r101_$TAG.log 2>&1
  echo "$TAG: $(grep '^exit' $L/r101_$TAG.log)"
done
/workspace/venv312/bin/python - <<'EOF'
import json
ROW = "llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager"
REC = {"run_roots": ["7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5"], "program": "079ee0a8e3e0355b", "manifest": "368283add1a11808"}
print("record", REC)
for tag in ("head", "base"):
    d = f"/workspace/cp/sweep-{tag}/{ROW}"
    try:
        v = json.load(open(f"{d}/commit/verdict.json"))
    except Exception as e:
        print(tag, "no verdict:", e); continue
    rm = v.get("required_manifest") or {}
    cs = {}
    try:
        cs = (json.load(open(f"{d}/commit_summary.json")).get("collector") or {})
    except Exception:
        pass
    print(tag, "run_roots", v.get("run_roots"), "== record:", v.get("run_roots") == REC["run_roots"], "| commit_pass", v.get("commit_pass"),
          "| program", (rm.get("program_digest") or "")[:16], "manifest", (rm.get("manifest_digest") or "")[:16],
          "| collector layout", cs.get("layout"), "| first_fail", v.get("first_fail_reason"))
EOF
echo "done $(date -u +%FT%TZ)"
