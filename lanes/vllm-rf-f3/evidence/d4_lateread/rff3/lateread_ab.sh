#!/bin/bash
# D4 behaviour check: canary.sh's lateread negative (SmolLM2 B1 256/32, --late-read qkv_proj) from the head tree, then the base tree.
# Expected: run roots equal head == base and != known-good cb129578... (the negative still detects the late read);
# acquisition_plan.json differs (head's plan lists the declared flush leaves; base's read the collector table after --late-read rebound it).
#   logs: /workspace/rff3/logs/lateread_{head,base}.log   out: /workspace/cp/lateread-{head,base}/
ROW=smollm2-135m__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager
L=/workspace/rff3/logs; mkdir -p $L
for pair in head:/workspace/head base:/workspace/basetree; do
  TAG=${pair%%:*}; T=${pair#*:}
  (
    cd "$T/integrations/vllm" || exit 3
    unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
    export PYTHONPATH=.:$T/packages/verity/src:$T/tools/research/src HF_HOME=/workspace/hf HF_HUB_OFFLINE=1 VLLM_BATCH_INVARIANT=1 \
           TOKENIZERS_PARALLELISM=false CUDA_HOME=/usr/local/cuda NATIVE_COLLECT_BUILD=/workspace/cp/nc_build
    PY=/workspace/venv312/bin/python; export PATH=$(dirname $PY):/usr/local/cuda/bin:$PATH
    HIDDEN_SO=/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so
    D=/workspace/cp/lateread-$TAG; rm -rf "$D"
    echo "start $(date -u +%FT%TZ) tree $T $(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["commit"])' $T/.research-source.json)"
    timeout 1500 $PY -m verity_vllm.harness.commit_delta --case B0 --workload workloads/$ROW.json --committer native_collect_v2b --fast-copy \
      --gpu-tree --openings 64 --pairs 1 --warmup 1 --max-num-seqs 1 --engine-arg max_model_len=288 --engine-arg gpu_memory_utilization=0.5 \
      --label rff3_lateread_$TAG --out "$D" --hidden-so "$HIDDEN_SO" --late-read qkv_proj
    echo "exit $? $(date -u +%FT%TZ)"
  ) > $L/lateread_$TAG.log 2>&1
  echo "$TAG: $(grep '^exit' $L/lateread_$TAG.log)"
done
/workspace/venv312/bin/python - <<'EOF'
import hashlib, json
r = {}
for tag in ("head", "base"):
    d = f"/workspace/cp/lateread-{tag}"
    try:
        v = json.load(open(f"{d}/verdict.json"))
    except Exception as e:
        print(tag, "no verdict:", e); continue
    try:
        plan = open(f"{d}/acquisition_plan.json", "rb").read()
        pd = hashlib.sha256(plan).hexdigest()[:16]
        pj = json.loads(plan)
    except Exception as e:
        pd, pj = f"no plan ({e})", {}
    r[tag] = (v.get("run_roots"), pd, pj)
    print(tag, "run_roots", v.get("run_roots"), "commit_pass", v.get("commit_pass"), "first_fail", v.get("first_fail_reason"), "| plan sha", pd)
if len(r) == 2:
    print("roots equal:", r["head"][0] == r["base"][0], "| plan equal:", r["head"][1] == r["base"][1])
    def walk(a, b, p=""):
        if type(a) != type(b): print("  diff", p, str(a)[:200], "|", str(b)[:200]); return
        if isinstance(a, dict):
            for k in sorted(set(a) | set(b)): walk(a.get(k), b.get(k), f"{p}/{k}")
        elif isinstance(a, list) and len(a) == len(b):
            for i, (x, y) in enumerate(zip(a, b)): walk(x, y, f"{p}[{i}]")
        elif a != b: print("  diff", p, str(a)[:300], "|", str(b)[:300])
    walk(r["head"][2], r["base"][2])
EOF
echo "done $(date -u +%FT%TZ)"
