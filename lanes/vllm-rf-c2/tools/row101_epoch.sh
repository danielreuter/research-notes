#!/bin/bash
# GPU spot row #101 at the epoch tree (/workspace/epoch, synced, uncommitted or committed): `row_pod.sh build,match,commit`
# PAIRS=1, as row101.sh; the bootstrap of the head/base run is reused.  Compared with the record and the pre-epoch head.
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
L=${RESEARCH_RUN_DIR:-/workspace/c2/r101e}; mkdir -p $L
[ -e /workspace/bootstrap/.c2-gpu-ok ] || { echo "no bootstrap"; exit 3; }
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
cat /workspace/epoch/.research-source.json 2>/dev/null; echo
(
  cd /workspace/epoch/integrations/vllm || exit 3
  unset VERITOR_REPO VERITY_LAYOUT VERITY_LEAF_LAYOUT
  export SWEEP_DIR=/workspace/cp/sweep-epoch PAIRS=1
  rm -rf "$SWEEP_DIR/$ROW"
  echo "start $(date -u +%FT%TZ) tree /workspace/epoch"
  env | sort | grep -E '^(VERITY|VERITOR|PY|SWEEP|PAIRS|HF_|CUDA|NATIVE|HIDDEN|GPU_UTIL|MAX_JOBS)'
  bash verity_vllm/ops/row_pod.sh $ROW LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da build,match,commit
  rc=$?
  echo "exit $rc $(date -u +%FT%TZ)"
  cat "$SWEEP_DIR/$ROW/stages.txt"
) > $L/r101_epoch.log 2>&1
echo "epoch: $(grep '^exit' $L/r101_epoch.log)"
/workspace/venv312/bin/python - "$L" <<'PY'
import glob, json, sys
ROW = "llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager"
REC = {"run_roots": ["7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5"], "program": "ccc213475e7c4eed", "manifest": "90f8186879d5035a"}
print("record / pre-epoch head", REC)
out = {}
for tag in ("epoch", "head"):
    d = f"/workspace/cp/sweep-{tag}/{ROW}"
    try:
        v = json.load(open(f"{d}/commit/verdict.json"))
    except Exception as e:
        print(tag, "no verdict:", e); continue
    rm = v.get("required_manifest") or {}
    bs = {}
    try:
        bs = json.load(open(f"{d}/build_summary.json"))
    except Exception:
        pass
    out[tag] = {"run_roots": v.get("run_roots"), "commit_pass": v.get("commit_pass"), "program_digest": rm.get("program_digest"),
                "manifest_digest": rm.get("manifest_digest"), "first_fail_reason": v.get("first_fail_reason"),
                "build_summary": {k: (x.get("program_digest") if isinstance(x, dict) else None) for k, x in bs.items() if isinstance(x, dict)},
                "ampere_ids": sorted({i for p in glob.glob(f"{d}/build_request*/descriptor.json.gz")
                                      for i in __import__("json").load(__import__("gzip").open(p, "rt"))["definitions"] if "AmpereBF16TcDot16" in i})}
    print(tag, json.dumps(out[tag]))
json.dump(out, open(sys.argv[1] + "/r101_epoch_summary.json", "w"), indent=1)
if len(out) == 2:
    print("epoch == pre-epoch head:", {k: out["epoch"][k] == out["head"][k] for k in ("run_roots", "commit_pass", "program_digest", "manifest_digest")})
PY
tar -czf $L/r101_epoch_outputs.tgz -C /workspace/cp --exclude='*.safetensors' --exclude='*.bin' --exclude='*.pt' \
  $(cd /workspace/cp && ls -d sweep-epoch/$ROW/{build,match,commit}/*.json sweep-epoch/$ROW/stages.txt sweep-epoch/$ROW/build_summary.json 2>/dev/null) 2>/dev/null
echo "done $(date -u +%FT%TZ)"
