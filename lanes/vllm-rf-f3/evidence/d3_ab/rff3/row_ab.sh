#!/bin/bash
# D3 A/B: the SmolLM2 B1 256/32 row (row_pod.sh build,match,commit, PAIRS=1) from the head tree, then from the base tree, on this L40S.
#   usage: row_ab.sh            logs: /workspace/rff3/logs/row_{head,base}.log   rows: /workspace/cp/sweep-{head,base}/<row>/
ROW=smollm2-135m__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager
L=/workspace/rff3/logs; mkdir -p $L
while pgrep -f pod_bootstrap.sh >/dev/null; do sleep 20; done
grep -q '^BOOTSTRAP-OK' /workspace/rff3/bootstrap.log || { echo "bootstrap not OK: $(tail -2 /workspace/rff3/bootstrap.log)"; exit 3; }
echo "bootstrap OK $(date -u +%FT%TZ)"
for pair in head:/workspace/head base:/workspace/basetree; do
  TAG=${pair%%:*}; T=${pair#*:}
  (
    cd "$T/integrations/vllm" || exit 3
    unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
    export SWEEP_DIR=/workspace/cp/sweep-$TAG PAIRS=1
    echo "start $(date -u +%FT%TZ) tree $T $(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["commit"])' $T/.research-source.json)"
    env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL)'
    bash verity_vllm/ops/row_pod.sh $ROW B0 HuggingFaceTB/SmolLM2-135M 93efa2f097d58c2a74874c7e644dbc9b0cee75a2 build,match,commit
    rc=$?
    echo "exit $rc $(date -u +%FT%TZ)"
    cat "$SWEEP_DIR/$ROW/stages.txt"
  ) > $L/row_$TAG.log 2>&1
  echo "$TAG: $(grep '^exit' $L/row_$TAG.log)"
done
echo "done $(date -u +%FT%TZ)"
