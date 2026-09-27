#!/usr/bin/env bash
# vo_run74.sh: task 3, row #74 (Qwen3-4B-FP8, H100 SXM5, TP1, B=8), on the shipped verification merge.  One real Build with the row's own
# declared target (sm_90, 132 SMs, fp8_block_gemm cutlass): `off` (nothing opted in: must equal the record, so its Programs ARE the
# recorded ones, art:9d14bd11).  Then on its 9 request Programs and its step Program, as built and with SHARED_SCALE substituted:
# query.cross_call, and the partition checker (Q_word_v1{16,32,no-recompute} with #98's member check) on every distinct specialization.
set -u
L=$RESEARCH_RUN_DIR; T=$PWD; I=$L/inputs
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
[ -z "${SETUP_RUN:-}" ] || grep -rqs --include='*.log' SMOKE-OK "$SETUP_RUN" || { echo "setup run has no SMOKE-OK: stop"; exit 3; }
ROW=qwen3-4b-fp8__fp8__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager; ROLE=QWEN3_4B_FP8; REPO=Qwen/Qwen3-4B-Instruct-2507-FP8
REV=8591804019c8b22094c3b5b4454e0edc05dffc98
bash "$I/vo_build.sh" r74-off "$ROW" "$ROLE" "$REPO" "$REV" '{"compute_capability": [9, 0], "fp8_block_gemm": "cutlass", "num_sms": 132}' "${JOBS:-6}"
export PATH=/workspace/venv312/bin:$PATH CUDA_VISIBLE_DEVICES=""
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd "$T/integrations/vllm"
R=/workspace/vo/sweep-r74-off/$ROW
D=$(for d in "$R"/build_request "$R"/build_request_LP* "$R"/build_step; do [ -f "$d/instances.json.gz" ] && echo "$d"; done)
E=$L/evidence/r74-off
M=verity_vllm.program.registry.fp8:SHARED_SCALE
python "$I/vo_calls.py" "$E/calls.jsonl" recorded $D
python "$I/vo_calls.py" "$E/calls.jsonl" shared-scale $D --map "$M"
python "$I/vo_word.py" "$E/word.jsonl" recorded "${WJOBS:-14}" $D
python "$I/vo_word.py" "$E/word.jsonl" shared-scale "${WJOBS:-14}" $D --map "$M"
python - "$E" <<'PY'
import json, sys
e = sys.argv[1]
calls = [json.loads(l) for l in open(f"{e}/calls.jsonl")]
word = [json.loads(l) for l in open(f"{e}/word.jsonl")]
out = {"digests_all_equal": json.load(open(f"{e}/digests.json"))["all_equal"],
       "cross_call": {c["label"]: c["total"] for c in calls if "total" in c},
       "word": {w["summary"]["label"]: {k: w["summary"][k] for k in ("specializations", "errors", "totals", "violations_by_class")}
                for w in word if "summary" in w}}
json.dump(out, open(f"{e}/../r74-summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
PY
echo "RUN74-DONE $(date -u +%FT%TZ)"
