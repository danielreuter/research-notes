#!/usr/bin/env bash
# vo_run57.sh: task 1, row #57 (Gemma-2-2B, L40S, TP1, B=8), on the shipped verification merge.  Two real Builds, concurrently, under the
# record's device target (sm_89, 142 SMs): `off` (weight_only_calls unset: must equal the record) and `once` (weight_only_calls =
# "once").  Then on both: query.cross_call on every request Program and the step Program, with the `+ 1` (AddScalarBf16_v1) and
# weight-only Call counts per Program.
set -u
L=$RESEARCH_RUN_DIR; T=$PWD; I=$L/inputs
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
[ -z "${SETUP_RUN:-}" ] || grep -rqs --include='*.log' SMOKE-OK "$SETUP_RUN" || { echo "setup run has no SMOKE-OK: stop"; exit 3; }
ROW=gemma2-2b__bf16__l40s__tp1__b8__i1024__o128__mixed__greedy__bi-eager; ROLE=GEMMA2_2B; REPO=unsloth/gemma-2-2b
REV=25319945f7fd83b8b903e12081777b7eef2ba993
bash "$I/vo_build.sh" r57-off "$ROW" "$ROLE" "$REPO" "$REV" '{"compute_capability": [8, 9], "num_sms": 142}' "${JOBS:-4}" &
bash "$I/vo_build.sh" r57-once "$ROW" "$ROLE" "$REPO" "$REV" '{"compute_capability": [8, 9], "num_sms": 142, "weight_only_calls": "once"}' "${JOBS:-4}" &
wait
export PATH=/workspace/venv312/bin:$PATH CUDA_VISIBLE_DEVICES=""
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd "$T/integrations/vllm"
for arm in off once; do
  R=/workspace/vo/sweep-r57-$arm/$ROW
  D=$(for d in "$R"/build_request "$R"/build_request_LP* "$R"/build_step; do [ -f "$d/instances.json.gz" ] && echo "$d"; done)
  python "$I/vo_calls.py" "$L/evidence/r57-$arm/calls.jsonl" "r57-$arm" $D
done
python - "$L/evidence" <<'PY'
import json, sys
ev = sys.argv[1]
out = {}
for arm in ("off", "once"):
    calls = [json.loads(l) for l in open(f"{ev}/r57-{arm}/calls.jsonl")]
    out[arm] = {"programs": {c["program"].rsplit("/", 1)[-1]: {k: c[k] for k in ("ok", "calls", "recomputed_gates", "plus_one_calls")} |
                             {"recomputes": c["recomputes"], "weight_only": c["weight_only_calls"]} for c in calls if "program" in c},
                "total": next(c["total"] for c in calls if "total" in c),
                "digests_all_equal": json.load(open(f"{ev}/r57-{arm}/digests.json"))["all_equal"]}
json.dump(out, open(f"{ev}/r57-summary.json", "w"), indent=1)
print(json.dumps({a: {"total": v["total"], "digests_all_equal": v["digests_all_equal"]} for a, v in out.items()}, indent=1))
PY
echo "RUN57-DONE $(date -u +%FT%TZ)"
