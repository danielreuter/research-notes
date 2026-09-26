#!/usr/bin/env bash
# gm_row101.sh: #101 on this L40S.  (1) Build -> Match -> Commit with the guarded-max tap OFF (GUARDED_MAX_TAP=0, the record's configuration:
# Program, manifest and run root must equal the record's); (2) the Commit alone with the tap ON (GUARDED_MAX_TAP=1: the manifest rebuilt
# under the guarded-max policy, the guarded FA2 tap build: a different run root, never the record), dumping step 0's FA2 layer-0 stream
# (VERITY_DUMP_STEP=0) so ROW word 3 is checked in the committed bytes.  PAIRS=1, VU_EXPORT=0 (neither moves a digest).  No HIDDEN_SO: the
# machine defaults pick the default / guarded build by the flag.  Evidence under $RESEARCH_RUN_DIR/evidence/{off,on}.
set -u
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager; ROLE=LLAMA32_1B; REPO=unsloth/Llama-3.2-1B
REV=9535bd9b1d1dea6acafbdc4813b728796aeb28da
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence/off" "$OUT/evidence/on"
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
unset HIDDEN_SO
export SWEEP_DIR=/workspace/gm/sweep PAIRS=1 VU_EXPORT=0 NORM_TAP=0
R=$SWEEP_DIR/$ROW
keep() { cp "$R/stages.txt" "$R/verdict.json" "$R/manifest.json" "$R/build_summary.json" "$R/row.log" "$1/" 2>/dev/null
         find "$R/commit" -maxdepth 1 -name '*.json' -size -5M -exec cp {} "$1/" \; 2>/dev/null; cp "$R/commit.log" "$1/" 2>/dev/null; }
rm -rf "$R"
GUARDED_MAX_TAP=0 verity-vllm row run "$ROW" "$ROLE" "$REPO" "$REV" --stages build,match,commit > "$OUT/row_off.log" 2>&1; echo "row off rc $? $(date -u +%FT%TZ)"
keep "$OUT/evidence/off"; tail -n 4 "$R/stages.txt"
VERITY_DUMP_STEP=0 GUARDED_MAX_TAP=1 verity-vllm row run "$ROW" "$ROLE" "$REPO" "$REV" --stages commit > "$OUT/row_on.log" 2>&1
echo "row on rc $? $(date -u +%FT%TZ)"
keep "$OUT/evidence/on"; cp "$R"/manifest.guarded-max-*.json "$OUT/evidence/on/" 2>/dev/null; tail -n 5 "$R/stages.txt"
find "$R/commit" -maxdepth 1 -name 'dump_step0_pair0_*L0*' \( -name '*ROW*' -o ! -name '*_s[0-9]*' \) -name '*.bin' -exec cp {} "$OUT/evidence/on/" \; 2>/dev/null
cp "$R"/commit/dump_step0_pair0_layout.json "$OUT/evidence/on/" 2>/dev/null
python - "$OUT/evidence" <<'PY'
import glob, json, os, re, sys
import numpy as np
from verity_vllm.program.kernels.derived_rows import guard_neg_inf_zero
ev = sys.argv[1]
REC = {"program": "ccc213475e7c4eed04b3b0d3717e2144012be65f41d900a018dbd09d1e400c6b", "manifest": "90f8186879d5035af027259151b4ac465bf6c3dcf08c1e6d62dab9b680bfeaac",
       "root": "7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5"}
out = {}
for arm in ("off", "on"):
    try:
        v = json.load(open(f"{ev}/{arm}/verdict.json")); m = json.load(open(f"{ev}/{arm}/manifest.json"))
    except Exception as e:
        out[arm] = {"error": repr(e)}; continue
    out[arm] = {"outcome": v.get("outcome"), "program": v.get("program_digest"), "manifest": m.get("manifest_digest"), "run_roots": v.get("run_roots"),
                "identities": len(m.get("identities") or []), "guarded_max": (m.get("query") or {}).get("guarded_max")}
off, on = out.get("off", {}), out.get("on", {})
out["off_equals_record"] = {"program": off.get("program") == REC["program"], "manifest": off.get("manifest") == REC["manifest"],
                            "run_root": bool(off.get("run_roots")) and all(r == REC["root"] for r in off["run_roots"])}
out["on_differs_from_record"] = bool(on.get("run_roots")) and all(r != REC["root"] for r in on["run_roots"])
out["on_identities_equal_off"] = on.get("identities") == off.get("identities") and on.get("manifest") == off.get("manifest")
# step 0 (the prefill: 256 rows, sk = sq, kBlockM 64, kBlockN 128) of attention layer 0, as committed: ROW word 3 at every entry
dumps = []
for f in sorted(glob.glob(f"{ev}/on/dump_step0_pair0_*.bin")):
    g = re.search(r"_g(\d+)x(\d+)x(\d+)(?:x(\d+)x(\d+))?(_ROW)?\.bin$", f)
    if not g:
        continue
    h, sl, nb = int(g[1]), int(g[2]), int(g[3]); bn = int(g[4] or 128); d = int(g[5] or 64)
    w = np.fromfile(f, dtype=np.uint32)
    if not g[6]:                                         # the whole M1 buffer: S, P, RP, then ROW
        n = nb * bn; off_row = h * sl * n * 2 + h * sl * (n // 2); w = w[off_row: off_row + h * sl * nb * 8]
    R = w.reshape(h, sl, nb, 8)
    later = first = bad = nonzero = 0
    for r in range(sl):
        nbm = min(nb, -(-((r // 64 + 1) * 64) // bn))
        first += h; nonzero += int(np.count_nonzero(R[:, r, nbm - 1, 3]))
        for b in range(nbm - 1):
            later += h; bad += int(np.count_nonzero(R[:, r, b, 3] != guard_neg_inf_zero(R[:, r, b, 0])))
    dumps.append({"file": os.path.basename(f), "heads": h, "rows": sl, "guard_words": later, "guard_mismatch": bad, "first_blocks": first,
                  "first_block_nonzero": nonzero})
out["committed_step0_layer0"] = dumps or "no dump"
json.dump(out, open(f"{ev}/summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
PY
echo "GM-ROW101-DONE $(date -u +%FT%TZ)"
