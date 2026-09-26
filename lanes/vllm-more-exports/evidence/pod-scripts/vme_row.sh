#!/usr/bin/env bash
# vme_row.sh N ROW ROLE REPO REV [CASES]: vllm-vu-export's vux_row.sh / vux_redraw.sh recipe for one row, from the shipped tree
# (research run --cwd source): bootstrap; the exporter's tests + lints in the background; Build -> Match -> Commit (PAIRS=1,
# BUILD_JOBS from the caller, default auto) with the default-on VU export ($RESEARCH_RUN_DIR/vu-export/<row>; limits-<N>.json from
# the run's inputs when sent); verify the store and the sets; the row's program.json (exported VUs placed through the store).
set -u
N=$1; ROW=$2; ROLE=$3; REPO=$4; REV=$5; CASES=${6:-B0,$ROLE}
T=$PWD; I=$RESEARCH_RUN_DIR/inputs; OUT=$RESEARCH_RUN_DIR; E=$OUT/vu-export/$ROW; mkdir -p "$E" "$OUT/evidence"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs VUX_REPO=$T/integrations/vllm
python -c "import verity_sampled_proofs; print('verity_sampled_proofs importable')"
cd integrations/vllm
while pgrep -f "pod_bootstrap.sh" > /dev/null; do sleep 15; done       # a bootstrap run already on the pod (its own research run)
bash verity_vllm/ops/pod_bootstrap.sh --cases "$CASES" --out "/workspace/vme/bootstrap-$N" > "$OUT/bootstrap.log" 2>&1; echo "bootstrap rc $? $(date -u +%FT%TZ)"
TESTS=""
[ "${RUN_TESTS:-1}" = 1 ] && { ( cd "$T" && bash "$I/vme_tests.sh" > "$OUT/tests.log" 2>&1; echo "tests: $(grep -cE '^(FAILED|ERROR)' "$OUT/tests.log") failed/errors $(date -u +%FT%TZ)" >> "$OUT/tests.log" ) & TESTS=$!; }
[ -f "$I/limits-$N.json" ] && cp "$I/limits-$N.json" "$E/limits.json" && echo "limits $(cat "$E/limits.json")"
export SWEEP_DIR=/workspace/vme/sweep-$N PAIRS=1 BUILD_JOBS=${BUILD_JOBS:-auto}
STAGES=${STAGES:-build,match,commit}
case ",$STAGES," in *,build,*) rm -rf "$SWEEP_DIR/$ROW";; *) echo "resuming over the Build in $SWEEP_DIR/$ROW";; esac
echo "row start STAGES=$STAGES BUILD_JOBS=$BUILD_JOBS MATCH_SNAP_MAX_BYTES=${MATCH_SNAP_MAX_BYTES:-derived} $(date -u +%FT%TZ)"
verity-vllm row run "$ROW" "$ROLE" "$REPO" "$REV" --stages "$STAGES" < /dev/null > "$OUT/row.log" 2>&1; echo "row rc $? $(date -u +%FT%TZ)"
R=$SWEEP_DIR/$ROW
cp "$R/stages.txt" "$R/verdict.json" "$R/row.log" "$R/admission.json" "$R/timeline.jsonl" "$R/build_summary.json" "$OUT/evidence/" 2>/dev/null
cp "$R/commit/sampled_replay_p0.json" "$OUT/evidence/" 2>/dev/null
cat "$R/stages.txt" 2>/dev/null
grep -rh "\[vu-export\]" "$R" 2>/dev/null | tail -3
if [ -f "$E/export.json" ]; then
  python -m verity_vllm.pipeline.cli vu-store verify "$E/store" < /dev/null > "$OUT/evidence/verify_store.json"; echo "verify_store rc $?"
  python - "$E" "$OUT/evidence" <<'PY'
import json, sys
from verity_vllm.pipeline import vu_export as V
e, ev = sys.argv[1], sys.argv[2]
v = json.load(open(ev + "/verdict.json")); print("verdict", v.get("outcome"), v.get("program_digest", "")[:16], v.get("manifest_digest", "")[:16], [r[:16] for r in v.get("run_roots") or []])
s = json.load(open(e + "/export.json")); print("limits", s["limits"], "store", s["store"], "wall_s", s["wall_s"])
for f, c in s["by_family"].items(): print("family", f, json.dumps(c))
for x in s["sets"]: print("set", x["set"], x["n"], x["bytes"], x["content_digest"][:16])
r = V.verify(e); json.dump(r, open(ev + "/verify_sets.json", "w"), indent=1); print("VERIFY", "OK" if r["ok"] else "FAIL", [(x["set"], x.get("bad_n")) for x in r["sets"] if not x["ok"]])
PY
  [ "${SKIP_GRAPH:-0}" = 1 ] || python "$I/program_graphs.py" "$OUT/program-graphs" "$ROW" "$R" --record "$R/commit/sampled_replay_p0.json" --vus "$E/vus.jsonl" --store "$E/store" \
    --run "${RESEARCH_RUN_ID:-}" --row "$N" --klass "PASS on run ${RESEARCH_RUN_ID:-}" < /dev/null; echo "program_graph rc $? $(date -u +%FT%TZ)"
else
  echo "NO EXPORT (see row.log / commit logs)"
fi
[ -n "$TESTS" ] && { wait "$TESTS"; tail -4 "$OUT/tests.log"; }
echo "VME-DONE $(date -u +%FT%TZ)"
