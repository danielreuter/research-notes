#!/bin/bash
# D4 behaviour check, v2: canary.sh's lateread negative as written (canary BASE args) is refused at head AND base ("FUSE: the acquisition
# plan needs --required-manifest and a hooking committer", exit 3), so this reruns the row's own Commit (row_pod.sh's commit_delta argv from
# <row>/commit.log, each tree against its own row dir) + --late-read qkv_proj, head then base.
# Expected: run roots head == base and != known-good cb129578...; acquisition_plan.json differs (head's plan lists the declared flush leaves,
# base's plan read the collector table after --late-read rebound it); the verdicts otherwise the same.
#   logs: /workspace/rff3/logs/lateread2_{head,base}.log   out: /workspace/cp/lateread2-{head,base}/commit/
ROW=smollm2-135m__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager
L=/workspace/rff3/logs; mkdir -p $L
for pair in head:/workspace/head base:/workspace/basetree; do
  TAG=${pair%%:*}; T=${pair#*:}; R=/workspace/cp/sweep-$TAG/$ROW; D=/workspace/cp/lateread2-$TAG
  (
    cd "$T/integrations/vllm" || exit 3
    unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
    export PYTHONPATH=.:$T/packages/verity/src:$T/tools/research/src HF_HOME=/workspace/hf HF_HUB_OFFLINE=1 VLLM_BATCH_INVARIANT=1 \
           TOKENIZERS_PARALLELISM=false CUDA_HOME=/usr/local/cuda NATIVE_COLLECT_BUILD=/workspace/cp/nc_build MATCH_IMPL=fast MATCH_PIPELINE=shared
    PY=/workspace/venv312/bin/python; export PATH=$(dirname $PY):/usr/local/cuda/bin:$PATH
    PD=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["request"]["program_digest"])' $R/build_summary.json)
    rm -rf "$D"; mkdir -p "$D"
    echo "start $(date -u +%FT%TZ) tree $T $(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["commit"])' $T/.research-source.json) program $PD"
    timeout 1500 $PY -m verity_vllm.harness.commit_delta --case B0 --workload workloads/$ROW.json --committer native_collect_v2b --fast-copy --gpu-tree \
      --hidden-so /workspace/cp/fa2/build/matReq/verity_fa2_matReq.so --openings 64 --pairs 1 --warmup 2 --max-num-seqs 1 \
      --engine-arg gpu_memory_utilization=0.5 --label rff3_lateread2_$TAG --out $D/commit --window-mb 256 --window-slots 8 --retain host \
      --open-after-release --tap-cap-mb 2048 --replay-cache --required-manifest $R/manifest.json --program-digest $PD --match-dir $R/match \
      --program-dir $R/build_request --weights-of-record $R/build_request/weights_of_record.json --late-read qkv_proj
    echo "exit $? $(date -u +%FT%TZ)"
  ) > $L/lateread2_$TAG.log 2>&1
  echo "$TAG: $(grep '^exit' $L/lateread2_$TAG.log)"
done
/workspace/venv312/bin/python - <<'EOF'
import hashlib, json
ROW = "smollm2-135m__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager"
r = {}
for tag in ("head", "base"):
    d = f"/workspace/cp/lateread2-{tag}/commit"
    try:
        v = json.load(open(f"{d}/verdict.json"))
    except Exception as e:
        print(tag, "no verdict:", e); continue
    ref = json.load(open(f"/workspace/cp/sweep-{tag}/{ROW}/commit/verdict.json"))
    try:
        plan = open(f"{d}/acquisition_plan.json", "rb").read(); pd = hashlib.sha256(plan).hexdigest()[:16]; pj = json.loads(plan)
    except Exception as e:
        pd, pj = f"no plan ({e})", {}
    r[tag] = (v.get("run_roots"), pd, pj, v)
    print(tag, "run_roots", v.get("run_roots"), "(row positive", ref.get("run_roots"), ") commit_pass", v.get("commit_pass"),
          "| first_fail", str(v.get("first_fail_reason"))[:300], "| plan sha", pd)
if len(r) == 2:
    print("roots equal head/base:", r["head"][0] == r["base"][0], "| plan equal:", r["head"][1] == r["base"][1],
          "| first_fail equal:", r["head"][3].get("first_fail_reason") == r["base"][3].get("first_fail_reason"))
    def walk(a, b, p=""):
        if type(a) != type(b): print("  plan diff", p, str(a)[:200], "|", str(b)[:200]); return
        if isinstance(a, dict):
            for k in sorted(set(a) | set(b)): walk(a.get(k), b.get(k), f"{p}/{k}")
        elif isinstance(a, list) and len(a) == len(b):
            for i, (x, y) in enumerate(zip(a, b)): walk(x, y, f"{p}[{i}]")
        elif a != b: print("  plan diff", p, str(a)[:400], "|", str(b)[:400])
    walk(r["head"][2], r["base"][2])
EOF
echo "done $(date -u +%FT%TZ)"
