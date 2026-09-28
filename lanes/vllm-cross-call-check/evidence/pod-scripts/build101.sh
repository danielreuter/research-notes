#!/usr/bin/env bash
# Row #101's Build products from one shipped tree: the request Program (LP 256, T 31), the workload Program, the required-value
# manifest and the program graph. Run from the tree's integrations/vllm on a bootstrapped L40S pod (ops/pod_bootstrap.sh --cases LLAMA32_1B):
#   research run --on <pod> --project verity --source <tree> --cwd source/integrations/vllm --send build101.sh \
#       -- bash '$RESEARCH_RUN_DIR/inputs/build101.sh'
# The workload declares no target, so the Build reads it from the host's GPU as the record Build did on its L40S (sm_89, 142 SMs);
# TARGET='<json>' declares one instead. The environment is the row driver's (row_driver.setup).
set -uo pipefail
OUT=${1:-${RESEARCH_RUN_DIR:?}/out}
ROOT=$(pwd -P)
export HF_HOME=${HF_HOME:-/workspace/hf} HF_HUB_OFFLINE=1 VLLM_BATCH_INVARIANT=1 TOKENIZERS_PARALLELISM=false VERITOR_REPO=$ROOT
export PYTHONPATH=.:$(cd ../../packages/verity/src && pwd -P):$(cd ../../tools/research/src && pwd -P)
PY=${PY:-/workspace/venv312/bin/python}
export PATH=$(dirname "$PY"):$PATH
WL=workloads/llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager.json
REPO=unsloth/Llama-3.2-1B
REV=9535bd9b1d1dea6acafbdc4813b728796aeb28da
CK=$HF_HOME/hub/models--unsloth--Llama-3.2-1B/snapshots/$REV
mkdir -p "$OUT"
cli() { "$PY" -m verity_vllm.pipeline.cli "$@"; }
step() { local name=$1; shift; echo "[build101] $(date -u +%FT%TZ) $name"; "$@" > "$OUT/$name.log" 2>&1; echo "[build101] $name rc=$?"; }

step build_request cli build --model $REPO --revision $REV --wrapper request --LP 256 --T 31 --max-model-len 288 --workload $WL \
    ${TARGET:+--target "$TARGET"} --out "$OUT/build_request"
step build_workload cli global-program --workload $WL --derived "$OUT/build_request" --out "$OUT/build_workload" --checkpoint-dir "$CK"
step manifest cli manifest build --program "$OUT/build_request" --workload $WL --out "$OUT/manifest.json"
step program_graph cli program-graph "$OUT/program_graph.json" "$OUT/build_request/instances.json.gz"

"$PY" - "$OUT" <<'EOF' | tee "$OUT/digests.json"
import hashlib, json, os, sys
o = sys.argv[1]
def load(p):
    try:
        return json.load(open(os.path.join(o, p)))
    except (OSError, ValueError):
        return {}
def sha(p):
    try:
        return hashlib.sha256(open(os.path.join(o, p), "rb").read()).hexdigest()
    except OSError:
        return None
r, w, m = load("build_request/result.json"), load("build_workload/workload_program.json"), load("manifest.json")
art = load("build_request/artifact.json")
print(json.dumps({"program_digest": (r.get("program") or {}).get("digest"), "ok": r.get("ok"), "unsupported": r.get("unsupported"),
                  "inputs": (r.get("program") or {}).get("inputs"), "sampling": r.get("sampling"),
                  "construction_version": (art.get("construction_version") or {}).get("sources_sha256"),
                  "workload_digest": w.get("workload_digest"), "manifest_digest": m.get("manifest_digest"),
                  "manifest_families": sorted((m.get("families") or {}).keys()) if isinstance(m.get("families"), dict) else None,
                  "program_graph_sha256": sha("program_graph.json"),
                  "descriptor_sha256": sha("build_request/descriptor.json.gz")}, indent=1, default=str))
EOF
