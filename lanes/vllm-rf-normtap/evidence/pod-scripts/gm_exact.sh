#!/usr/bin/env bash
# gm_exact.sh fa2|fa3: the FA-tap exactness property (tests/properties/fa_tap_exactness_gpu.py) on this GPU for the default tap build, then for
# the guarded-max build against the default build's record (--baseline): out/lse, closedness, negatives, and ROW word 3 = the IR's
# GuardNegInfZero_v1 of the entry's row_max after a row's first key block, every other stream word equal to the default build's.
# The tap builds are the ones pod_fa2_tap.sh / pod_fa3_tap.sh left (rebuilt only if their inputs changed).  Evidence: $RESEARCH_RUN_DIR/evidence.
set -u
T=$PWD; OUT=$RESEARCH_RUN_DIR; V=${1:?fa2 or fa3}; mkdir -p "$OUT/evidence/default" "$OUT/evidence/guarded"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
if [ "$V" = fa3 ]; then
  S=verity_vllm/ops/pod_fa3_tap.sh; B=/workspace/cp/fa2/build; SO=$B/fa3_matReq/verity_fa3_matReq.so; SOG=$B/fa3_matReqG/verity_fa3_matReqG.so
  bash $S > "$OUT/tap_default.log" 2>&1; echo "tap default rc $?"; tail -n 1 "$OUT/tap_default.log"
  FA3_TAP_ROW_GUARD=1 bash $S > "$OUT/tap_guarded.log" 2>&1; echo "tap guarded rc $?"; tail -n 1 "$OUT/tap_guarded.log"
else
  S=verity_vllm/ops/pod_fa2_tap.sh; B=/workspace/cp/fa2/build; SO=$B/matReq/verity_fa2_matReq.so; SOG=$B/matReqG/verity_fa2_matReqG.so
  bash $S > "$OUT/tap_default.log" 2>&1; echo "tap default rc $?"; tail -n 1 "$OUT/tap_default.log"
  FA2_TAP_ROW_GUARD=1 bash $S > "$OUT/tap_guarded.log" 2>&1; echo "tap guarded rc $?"; tail -n 1 "$OUT/tap_guarded.log"
fi
G=tests/properties/fa_tap_exactness_gpu.py
python $G --so "$SO" --out "$OUT/evidence/default" > "$OUT/exact_default.log" 2>&1; echo "default rc $? $(date -u +%FT%TZ)"; tail -n 1 "$OUT/exact_default.log"
python $G --so "$SOG" --baseline "$OUT/evidence/default/fa_tap_exactness.json" --out "$OUT/evidence/guarded" > "$OUT/exact_guarded.log" 2>&1
echo "guarded rc $? $(date -u +%FT%TZ)"; tail -n 1 "$OUT/exact_guarded.log"
grep -h -E -- "-> FAIL|Traceback|Error" "$OUT/exact_default.log" "$OUT/exact_guarded.log" | head -20
for r in default guarded; do python $G --verify "$OUT/evidence/$r/fa_tap_exactness.json"; done
python - "$OUT/evidence" <<'PY'
import json, sys
ev = sys.argv[1]
d, g = (json.load(open(f"{ev}/{k}/fa_tap_exactness.json")) for k in ("default", "guarded"))
by = {}
for e in g["cases"]:
    r = e.get("row3") or {}
    by.setdefault(e["D"], []).append((e["case"], e["ok"], r.get("guard_words"), r.get("guard_mismatch"), r.get("first_block_nonzero"),
                                     r.get("ir_mismatch"), r.get("ir_sampled"), r.get("stream_eq_baseline")))
out = {"default": {"ok": d["ok"], "digest": d["digest"], "so": d["tap"]["sha256"], "cases": len(d["cases"]), "negatives": len(d["negatives"])},
       "guarded": {"ok": g["ok"], "digest": g["digest"], "so": g["tap"]["sha256"], "cases": len(g["cases"]), "negatives": len(g["negatives"]),
                   "guard_words": sum(e["row3"]["guard_words"] for e in g["cases"] if e.get("row3")),
                   "cases_ok": sum(bool(e["ok"]) for e in g["cases"]), "negatives_ok": sum(bool(e["ok"]) for e in g["negatives"])},
       "per_head_dim": by}
json.dump(out, open(f"{ev}/summary.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("default", "guarded")}))
PY
echo "GM-EXACT-DONE $(date -u +%FT%TZ)"
