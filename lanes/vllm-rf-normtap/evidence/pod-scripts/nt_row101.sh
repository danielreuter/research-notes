#!/usr/bin/env bash
# nt_row101.sh: #101 on this L40S.  (1) Build -> Match -> Commit with the tap OFF (NORM_TAP=0, the record's configuration: Program, manifest
# and run root must equal the record's); (2) the Commit alone with the tap ON (NORM_TAP=1: the manifest rebuilt under the norm-scale policy,
# the tap attached: a different run root, never the record); (3) Q_word_v1{16,32} under the policy on the Build (--word-check, strict).
# PAIRS=1 and VU_EXPORT=0 (neither moves a digest).  Evidence under $RESEARCH_RUN_DIR/evidence/{off,on}.
set -u
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager; ROLE=LLAMA32_1B; REPO=unsloth/Llama-3.2-1B
REV=9535bd9b1d1dea6acafbdc4813b728796aeb28da
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence/off" "$OUT/evidence/on"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
bash verity_vllm/ops/pod_norm_tap.sh > "$OUT/norm_tap.log" 2>&1; echo "norm tap rc $?"; tail -n 1 "$OUT/norm_tap.log"
export HIDDEN_SO=/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so SWEEP_DIR=/workspace/nt/sweep PAIRS=1 VU_EXPORT=0
R=$SWEEP_DIR/$ROW
keep() { cp "$R/stages.txt" "$R/verdict.json" "$R/manifest.json" "$R/build_summary.json" "$R/row.log" "$1/" 2>/dev/null
         find "$R/commit" -maxdepth 1 -name '*.json' -size -5M -exec cp {} "$1/" \; 2>/dev/null; cp "$R/commit.log" "$1/" 2>/dev/null; }
rm -rf "$R"
NORM_TAP=0 verity-vllm row run "$ROW" "$ROLE" "$REPO" "$REV" --stages build,match,commit > "$OUT/row_off.log" 2>&1; echo "row off rc $? $(date -u +%FT%TZ)"
keep "$OUT/evidence/off"; cat "$R/stages.txt"
NORM_TAP=1 verity-vllm row run "$ROW" "$ROLE" "$REPO" "$REV" --stages commit > "$OUT/row_on.log" 2>&1; echo "row on rc $? $(date -u +%FT%TZ)"
keep "$OUT/evidence/on"; cp "$R"/manifest.no-norm-scales-*.json "$OUT/evidence/on/" 2>/dev/null; tail -n 5 "$R/stages.txt"
verity-vllm manifest build --program "$R/build_request" --workload "workloads/$ROW.json" --norm-scales --word-check 16/32 \
  --out "$OUT/evidence/on/manifest_word.json" > "$OUT/evidence/on/manifest_word.log" 2>&1; echo "word check (norm scales) rc $?"
tail -n 3 "$OUT/evidence/on/manifest_word.log"
python - "$OUT/evidence" <<'PY'
import json, sys
ev = sys.argv[1]
REC = {"program": "ccc213475e7c4eed04b3b0d3717e2144012be65f41d900a018dbd09d1e400c6b", "manifest": "90f8186879d5035af027259151b4ac465bf6c3dcf08c1e6d62dab9b680bfeaac",
       "root": "7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5"}
out = {}
for arm in ("off", "on"):
    try:
        v = json.load(open(f"{ev}/{arm}/verdict.json")); m = json.load(open(f"{ev}/{arm}/manifest.json"))
    except Exception as e:
        out[arm] = {"error": repr(e)}; continue
    ns = [r for r in m.get("identities", []) if r.get("family") == "norm_scales"]
    out[arm] = {"outcome": v.get("outcome"), "program": v.get("program_digest"), "manifest": m.get("manifest_digest"), "run_roots": v.get("run_roots"),
                "identities": len(m.get("identities") or []), "norm_scales_identities": len(ns), "norm_scales_words": sum(int(r.get("rows") or 0) for r in ns),
                "norm_scales_by_spec": {s: sum(int(r["rows"]) for r in ns if r.get("spec") == s) for s in sorted({r.get("spec") for r in ns})},
                "query_norm_scales": (m.get("query") or {}).get("norm_scales")}
off = out.get("off", {})
out["off_equals_record"] = {"program": off.get("program") == REC["program"], "manifest": off.get("manifest") == REC["manifest"],
                            "run_root": bool(off.get("run_roots")) and all(r == REC["root"] for r in off["run_roots"])}
on = out.get("on", {})
out["on_differs_from_record"] = bool(on.get("run_roots")) and all(r != REC["root"] for r in on["run_roots"])
try:
    out["word_check_manifest_equals_commit"] = json.load(open(f"{ev}/on/manifest_word.json"))["manifest_digest"] == on.get("manifest")
except Exception as e:
    out["word_check_manifest_equals_commit"] = repr(e)
json.dump(out, open(f"{ev}/summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
PY
echo "NT-ROW101-DONE $(date -u +%FT%TZ)"
