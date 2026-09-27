#!/usr/bin/env bash
# vo_run73.sh: task 2, row #73 (Qwen3-4B, H100 SXM5, TP1, B=8), on the shipped verification merge.  Two real Builds, concurrently, under the
# record's device target (sm_90, 132 SMs): `off` (fa3_construction unset: must equal the record) and `v4` (fa3_construction =
# "check-inf-per-iteration": Attention_v4).  Then on both: query.cross_call on every request Program and the step Program, and the
# partition checker (Q_word_v1{16,32,no-recompute} with #98's member check) on every distinct specialization, each cut exactly.
set -u
L=$RESEARCH_RUN_DIR; T=$PWD; I=$L/inputs
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '"state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
[ -z "${WAIT_RUN:-}" ] || grep -rqs --include='*.log' --include='*.txt' SMOKE-OK "$WAIT_RUN" || { echo "setup run has no SMOKE-OK: stop"; exit 3; }
ROW=qwen3-4b__bf16__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager; ROLE=QWEN3_4B; REPO=Qwen/Qwen3-4B-Instruct-2507
REV=cdbee75f17c01a7cc42f958dc650907174af0554
bash "$I/vo_build.sh" r73-off "$ROW" "$ROLE" "$REPO" "$REV" '{"compute_capability": [9, 0], "num_sms": 132}' "${JOBS:-4}" &
bash "$I/vo_build.sh" r73-v4 "$ROW" "$ROLE" "$REPO" "$REV" '{"compute_capability": [9, 0], "fa3_construction": "check-inf-per-iteration", "num_sms": 132}' "${JOBS:-4}" &
wait
export PATH=/workspace/venv312/bin:$PATH CUDA_VISIBLE_DEVICES=""
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd "$T/integrations/vllm"
for arm in off v4; do
  R=/workspace/vo/sweep-r73-$arm/$ROW
  D=$(for d in "$R"/build_request "$R"/build_request_LP* "$R"/build_step; do [ -f "$d/instances.json.gz" ] && echo "$d"; done)
  python "$I/vo_calls.py" "$L/evidence/r73-$arm/calls.jsonl" "r73-$arm" $D
  python "$I/vo_word.py" "$L/evidence/r73-$arm/word.jsonl" "r73-$arm" "${WJOBS:-14}" $D
done
python - "$L/evidence" <<'PY'
import json, sys
from collections import Counter
ev = sys.argv[1]
out = {}
for arm in ("off", "v4"):
    rows = [json.loads(l) for l in open(f"{ev}/r73-{arm}/word.jsonl")]
    fam = Counter()
    for r in rows:
        if "spec" in r and "error" not in r:
            fam[r["spec"].split("{")[0]] += r["calls"]
    summ = next(r["summary"] for r in rows if "summary" in r)
    calls = [json.loads(l) for l in open(f"{ev}/r73-{arm}/calls.jsonl")]
    out[arm] = {"word": summ, "attention_calls": {k: v for k, v in fam.items() if k.startswith("Attention")},
                "cross_call": next(c["total"] for c in calls if "total" in c),
                "digests_all_equal": json.load(open(f"{ev}/r73-{arm}/digests.json"))["all_equal"]}
json.dump(out, open(f"{ev}/r73-summary.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:4000])
PY
echo "RUN73-DONE $(date -u +%FT%TZ)"
