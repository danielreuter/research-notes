#!/usr/bin/env bash
# Row #101 at one tree: build,match (row_pod.sh) -> property records into <row>/properties/ (world-1 non-interference from the row's
# own Match arms + the three-process boundary-hash comparison; census reconciliation) -> commit (row_pod.sh; its from-record cites them).
# Run from integrations/vllm of the source tree.  PHASE=props,commit resumes after build,match.
set -u
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
REV=9535bd9b1d1dea6acafbdc4813b728796aeb28da
export SWEEP_DIR=${SWEEP_DIR:-/workspace/cp/sweep} PAIRS=${PAIRS:-1}
PHASE=${PHASE:-rowmatch,props,commit}
D=$SWEEP_DIR/$ROW
PY=/workspace/venv312/bin/python
stamp() { echo "[chain101] $(date -u +%FT%TZ) $*"; }

if [[ ,$PHASE, == *,rowmatch,* ]]; then
  stamp "row_pod.sh build,match"
  bash verity_vllm/ops/row_pod.sh "$ROW" LLAMA32_1B unsloth/Llama-3.2-1B "$REV" build,match; stamp "build,match rc=$?"
fi

if [[ ,$PHASE, == *,props,* ]]; then
  export PYTHONPATH=.:$(cd ../../packages/verity/src && pwd):$(cd ../../tools/research/src && pwd) HF_HOME=${HF_HOME:-/workspace/hf} HF_HUB_OFFLINE=1 \
         VLLM_BATCH_INVARIANT=1 TOKENIZERS_PARALLELISM=false CUDA_HOME=${CUDA_HOME:-/usr/local/cuda} PATH=$(dirname "$PY"):/usr/local/cuda/bin:$PATH
  CK=$(sed -n 's/.* ckpt=\(.*\) stages=.*/\1/p' "$D/row.log" | tail -1)
  P=$D/props_run
  CMD=($PY -m verity_vllm.pipeline.match --case LLAMA32_1B --workload "workloads/$ROW.json" --out "$P" --checkpoint-dir "$CK" --phase all
       --python-gpu "$PY" --python-cpu "$PY" --max-num-seqs 1 --control-tokens "$D/match/control/tokens.json" --log "$D/match/capture/log.jsonl.gz"
       --skip capture,control,resolve,compare,fold,root_policy,golden,wiring,replay,gates --engine-arg gpu_memory_utilization=0.5)
  stamp "props dry run (ckpt=$CK)"
  "${CMD[@]}" --dry-run
  stamp "props run"
  "${CMD[@]}" > "$D/props_run.log" 2>&1; stamp "props rc=$?"
  tail -30 "$D/props_run.log"
  $PY - "$D" "$ROW" <<'EOF'
import json, sys
from pathlib import Path
from verity_vllm.properties import noninterference as N
from verity_vllm.properties.record import PropertyRecord
d, row = Path(sys.argv[1]), sys.argv[2]
p = d / "props_run"
docs = [N.record(d / "match", 1, run=row, hashes=p / "nonint" / "noninterference.json")]
cr = p / "census_reconcile.json"
docs.append(json.loads(cr.read_text()) if cr.is_file() else None)
for doc in docs:
    if doc is None:
        print("no census_reconcile.json"); continue
    r = PropertyRecord(doc)
    print(r.write(d), r.name, "ok" if r.ok else "NOT ok", r.digest, r.problems(), doc.get("problems"))
EOF
  stamp "records rc=$?"
fi

if [[ ,$PHASE, == *,commit,* ]]; then
  stamp "row_pod.sh commit"
  bash verity_vllm/ops/row_pod.sh "$ROW" LLAMA32_1B unsloth/Llama-3.2-1B "$REV" commit; stamp "commit rc=$?"
  $PY -c 'import json,sys; v=json.load(open(sys.argv[1])); print(v["outcome"], v.get("program_digest"), v.get("manifest_digest"), v.get("run_roots")); [print(c) for c in v.get("properties", [])]' "$D/verdict.json"
fi
