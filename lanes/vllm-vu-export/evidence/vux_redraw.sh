#!/usr/bin/env bash
# vux_redraw.sh: the branch's tests; then #101 and #4 Build -> Match -> Commit (PAIRS=1) with the default-on VU export (the store +
# its default extraction into $RESEARCH_RUN_DIR/vu-export/<row>); verify each store and its sets; each row's program.json (chunked
# edges, sampler VUs placed through the store) into $RESEARCH_RUN_DIR/program-graphs
set -u
T=$PWD; I=$RESEARCH_RUN_DIR/inputs; OUT=$RESEARCH_RUN_DIR
bash $I/vux_tests.sh > $OUT/tests.log 2>&1; echo "tests: $(grep -c '^FAILED\|^ERROR' $OUT/tests.log) failed/errors $(date -u +%FT%TZ)"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs VUX_REPO=$T/integrations/vllm
cd integrations/vllm
bash verity_vllm/ops/pod_bootstrap.sh --cases B0,LLAMA32_1B --out /workspace/vux/bootstrap > $OUT/bootstrap.log 2>&1; echo "bootstrap rc $? $(date -u +%FT%TZ)"
export HIDDEN_SO=/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so SWEEP_DIR=/workspace/vux/sweep PAIRS=1
while read -r N ROW ROLE REPO REV; do
  rm -rf "$SWEEP_DIR/$ROW"
  verity-vllm row run "$ROW" "$ROLE" "$REPO" "$REV" --stages build,match,commit < /dev/null > "$OUT/row-$N.log" 2>&1; echo "row $N rc $? $(date -u +%FT%TZ)"
  R=$SWEEP_DIR/$ROW; E=$OUT/vu-export/$ROW; mkdir -p "$OUT/evidence-$N"
  cp "$R/stages.txt" "$R/verdict.json" "$R/commit/sampled_replay_p0.json" "$OUT/evidence-$N/" 2>/dev/null
  grep -h "\[vu-export\]" "$R"/*.log "$R"/commit/*.log 2>/dev/null | tail -2
  python -m verity_vllm.pipeline.cli vu-store verify "$E/store" < /dev/null > "$OUT/evidence-$N/verify_store.json"; echo "verify_store rc $?"
  python - "$E" "$OUT/evidence-$N" <<'PY'
import json, sys
from verity_vllm.pipeline import vu_export as V
e, ev = sys.argv[1], sys.argv[2]
v = json.load(open(ev + "/verdict.json")); print("verdict", v.get("outcome"), v.get("program_digest", "")[:16], v.get("manifest_digest", "")[:16], [r[:16] for r in v.get("run_roots") or []])
s = json.load(open(e + "/export.json")); print("limits", s["limits"], "store", s["store"])
for f, c in s["by_family"].items(): print("family", f, json.dumps(c))
for x in s["sets"]: print("set", x["set"], x["n"], x["bytes"], x["content_digest"][:16])
r = V.verify(e); json.dump(r, open(ev + "/verify_sets.json", "w"), indent=1); print("VERIFY", "OK" if r["ok"] else "FAIL")
PY
  python $I/program_graphs.py $OUT/program-graphs "$ROW" "$R" --record "$R/commit/sampled_replay_p0.json" --vus "$E/vus.jsonl" --store "$E/store" \
    --run "${RESEARCH_RUN_ID:-}" --row "$N" --klass "PASS on run ${RESEARCH_RUN_ID:-}" < /dev/null
done <<'ROWS'
101 llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da
4 smollm2-135m__bf16__l40s__tp1__b16__i1024__o128__mixed__greedy__bi-eager B0 HuggingFaceTB/SmolLM2-135M 93efa2f097d58c2a74874c7e644dbc9b0cee75a2
ROWS
echo "REDRAW-DONE $(date -u +%FT%TZ)"
