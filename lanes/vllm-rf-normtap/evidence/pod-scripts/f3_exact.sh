#!/usr/bin/env bash
# f3_exact.sh fa3 (CONSTRUCTION=check-inf-per-iteration): ms_exact.sh with the guarded build also checked under FA3's per-iteration Check_inf
# construction (property (g): MS words vs AttnBlock_v4, every output row vs Attention_v4).  From ms_exact.sh: bootstrap this pod from the shipped tree (fa2: B0 + LLAMA32_1B, the default FA2 tap at hd 64/96/128/256; fa3: B0, FA2
# at hd 64 only), build the guarded-max tap (now VERITY_MAT_SRC=123: ROW word 3 + the MS class) beside the default one, then the FA-tap
# exactness property for the default build and for the guarded build against the default build's record (--baseline): out/lse, closedness
# (MS included), negatives, ROW word 3 = the IR's guard, every MS word = the IR's F32MulFtz(GuardNegInfZero(row_max), scale_log2), the six
# classes equal to the default build's.  Evidence: $RESEARCH_RUN_DIR/evidence.
#   research run --on <pod> --project verity --source <worktree> --cwd source --custody-r2 --send ms_exact.sh -- bash -c 'bash $RESEARCH_RUN_DIR/inputs/ms_exact.sh fa2'
set -u
T=$PWD; OUT=$RESEARCH_RUN_DIR; V=${1:?fa2 or fa3}; mkdir -p "$OUT/evidence/default" "$OUT/evidence/guarded"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv > "$OUT/evidence/gpu.txt" 2>&1; cat "$OUT/evidence/gpu.txt"
B=/workspace/cp/fa2/build
if [ "$V" = fa3 ]; then
  FA2_TAP_HDIMS=64 bash verity_vllm/ops/pod_bootstrap.sh --cases B0 --out /workspace/ms/bootstrap > "$OUT/bootstrap.log" 2>&1
  echo "bootstrap rc $? $(date -u +%FT%TZ)"; tail -n 3 "$OUT/bootstrap.log"
  S=verity_vllm/ops/pod_fa3_tap.sh; SO=$B/fa3_matReq/verity_fa3_matReq.so; SOG=$B/fa3_matReqG/verity_fa3_matReqG.so
  bash $S > "$OUT/tap_default.log" 2>&1; echo "tap default rc $?"; tail -n 1 "$OUT/tap_default.log"
  FA3_TAP_ROW_GUARD=1 bash $S > "$OUT/tap_guarded.log" 2>&1; echo "tap guarded rc $? $(date -u +%FT%TZ)"; tail -n 2 "$OUT/tap_guarded.log"
else
  bash verity_vllm/ops/pod_bootstrap.sh --cases B0,LLAMA32_1B --out /workspace/ms/bootstrap > "$OUT/bootstrap.log" 2>&1
  echo "bootstrap rc $? $(date -u +%FT%TZ)"; tail -n 3 "$OUT/bootstrap.log"
  S=verity_vllm/ops/pod_fa2_tap.sh; SO=$B/matReq/verity_fa2_matReq.so; SOG=$B/matReqG/verity_fa2_matReqG.so
  bash $S > "$OUT/tap_default.log" 2>&1; echo "tap default rc $?"; tail -n 1 "$OUT/tap_default.log"
  FA2_TAP_ROW_GUARD=1 bash $S > "$OUT/tap_guarded.log" 2>&1; echo "tap guarded rc $? $(date -u +%FT%TZ)"; tail -n 2 "$OUT/tap_guarded.log"
fi
for b in "$(dirname "$SO")" "$(dirname "$SOG")"; do cp "$b/build_info.json" "$OUT/evidence/$(basename "$b")_build_info.json" 2>/dev/null; done
G=tests/properties/fa_tap_exactness_gpu.py
python $G --so "$SO" --out "$OUT/evidence/default" > "$OUT/exact_default.log" 2>&1; echo "default rc $? $(date -u +%FT%TZ)"; tail -n 1 "$OUT/exact_default.log"
python $G --so "$SOG" --baseline "$OUT/evidence/default/fa_tap_exactness.json" ${CONSTRUCTION:+--construction $CONSTRUCTION} --out "$OUT/evidence/guarded" > "$OUT/exact_guarded.log" 2>&1
echo "guarded rc $? $(date -u +%FT%TZ)"; tail -n 1 "$OUT/exact_guarded.log"
grep -h -E -- "-> FAIL|Traceback|Error" "$OUT/exact_default.log" "$OUT/exact_guarded.log" | head -30
for r in default guarded; do python $G --verify "$OUT/evidence/$r/fa_tap_exactness.json"; done
python - "$OUT/evidence" <<'PY'
import json, sys
ev = sys.argv[1]
d, g = (json.load(open(f"{ev}/{k}/fa_tap_exactness.json")) for k in ("default", "guarded"))
by = {}
for e in g["cases"]:
    r, m = e.get("row3") or {}, e.get("ms") or {}
    by.setdefault(e["D"], []).append({"case": e["case"], "ok": e["ok"], "error": e.get("error"), "guard_words": r.get("guard_words"),
                                      "guard_mismatch": r.get("guard_mismatch"), "stream_eq_baseline": r.get("stream_eq_baseline"),
                                      "ms_words": m.get("ms_words"), "ms_mismatch": m.get("ms_mismatch"),
                                      "ms_mismatch_neg_inf_max": m.get("ms_mismatch_neg_inf_max"), "ms_ir": [m.get("ir_mismatch"), m.get("ir_sampled")],
                                      "first_mismatch": m.get("first_mismatch"), "spill": e.get("spill_outside_layout"),
                                      "unguarded": m.get("unguarded_words"), "out_vs_ir": e.get("out_vs_ir"),
                                      "unwritten": e.get("expected_but_unwritten")})
cs = g["cases"]
out = {"default": {"ok": d["ok"], "digest": d["digest"], "so": d["tap"]["sha256"], "src": d["tap"]["src"], "cases": len(d["cases"]),
                   "negatives": len(d["negatives"]), "cases_ok": sum(bool(e["ok"]) for e in d["cases"])},
       "guarded": {"ok": g["ok"], "digest": g["digest"], "so": g["tap"]["sha256"], "src": g["tap"]["src"], "cases": len(cs), "negatives": len(g["negatives"]),
                   "cases_ok": sum(bool(e["ok"]) for e in cs), "negatives_ok": sum(bool(e["ok"]) for e in g["negatives"]),
                   "guard_words": sum((e.get("row3") or {}).get("guard_words") or 0 for e in cs),
                   "ms_words": sum((e.get("ms") or {}).get("ms_words") or 0 for e in cs),
                   "ms_mismatch": sum((e.get("ms") or {}).get("ms_mismatch") or 0 for e in cs),
                   "ms_mismatch_neg_inf_max": sum((e.get("ms") or {}).get("ms_mismatch_neg_inf_max") or 0 for e in cs),
                   "ms_ir_mismatch": sum((e.get("ms") or {}).get("ir_mismatch") or 0 for e in cs),
                   "stream_eq_baseline": sum((e.get("row3") or {}).get("stream_eq_baseline") is True for e in cs),
                   "construction": g.get("construction"),
                   "unguarded_ms_words": sum((e.get("ms") or {}).get("unguarded_words") or 0 for e in cs),
                   "out_rows": sum((e.get("out_vs_ir") or {}).get("rows") or 0 for e in cs),
                   "out_heads": sum((e.get("out_vs_ir") or {}).get("heads") or 0 for e in cs),
                   "out_mismatch_heads": sum((e.get("out_vs_ir") or {}).get("mismatch") or 0 for e in cs),
                   "out_reference_heads": sum((e.get("out_vs_ir") or {}).get("reference_heads") or 0 for e in cs),
                   "out_unevaluated": sum((e.get("out_vs_ir") or {}).get("unevaluated") or 0 for e in cs)},
       "per_head_dim": by}
json.dump(out, open(f"{ev}/summary.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("default", "guarded")}))
for D, rows in by.items():
    for r in rows:
        if not r["ok"]:
            print("NOT-OK", D, json.dumps(r))
PY
echo "F3-EXACT-DONE $(date -u +%FT%TZ)"
