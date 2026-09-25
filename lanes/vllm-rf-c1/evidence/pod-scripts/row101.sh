#!/bin/bash
# GPU Commit row on a FROZEN regression row: #101 llama32-1b B1 256/32 stoch (l40s), `row_pod.sh build,match,commit` PAIRS=1 (its
# record's --pairs 1), from the head tree then the base tree, VERITY_(LEAF_)LAYOUT unset (f3's row101.sh, paths moved).  Compares the
# run root with #101's record (commit/verdict.json of art:a4ea1a18...: 7adcef49...) and the rebuilt Program / manifest digests head vs base
# (the record's 079ee0a8... / 368283ad... predate the relayout: no from-scratch Build gives them, f3 and f24).
#   usage: [PAIRS_TO_RUN="head:/workspace/head"] row101.sh      logs: /workspace/c1/logs/r101_{head,base}.log   rows: /workspace/cp/sweep-{head,base}/<row>/   summary: logs/row101.out
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
L=/workspace/c1/logs; mkdir -p $L
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK: $(tail -2 $L/bootstrap.log)"; exit 3; }
echo "bootstrap OK $(date -u +%FT%TZ)"
for pair in ${PAIRS_TO_RUN:-head:/workspace/head base:/workspace/basetree}; do
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
    print(tag, "run_roots", v.get("run_roots"), "== record:", v.get("run_roots") == REC["run_roots"], "| commit_pass", v.get("commit_pass"),
          "| program", rm.get("program_digest"), "manifest", rm.get("manifest_digest"), "| first_fail", v.get("first_fail_reason"))
EOF
echo "done $(date -u +%FT%TZ)"
