#!/usr/bin/env bash
# ms_row101.sh: #101 on this L40S.  (1) Build -> Match -> Commit with GUARDED_MAX_TAP=0 (the record's configuration: run root = the record's,
# manifest = the flag-off manifest of the current tree); (2) the Commit alone with GUARDED_MAX_TAP=1 (the manifest rebuilt under the policy,
# the guarded FA2 build with the MS class), twice, dumping attention layer 0's committed stream at step 0 (the prefill) and step 1 (a decode
# step) (VERITY_DUMP_STEP, --tensor-digests): the MS class (every visited word = the IR's F32MulFtz(GuardNegInfZero(row_max), scale_log2)) and
# ROW word 3 in the committed bytes, and both tap-on runs give one root.  PAIRS=1, VU_EXPORT=0.  Evidence under $RESEARCH_RUN_DIR/evidence.
set -u
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager; ROLE=LLAMA32_1B; REPO=unsloth/Llama-3.2-1B
REV=9535bd9b1d1dea6acafbdc4813b728796aeb28da
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence/off"
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
unset HIDDEN_SO
export SWEEP_DIR=/workspace/ms/sweep PAIRS=1 VU_EXPORT=0 NORM_TAP=0
R=$SWEEP_DIR/$ROW
keep() { cp "$R/stages.txt" "$R/verdict.json" "$R/manifest.json" "$R/build_summary.json" "$R/row.log" "$1/" 2>/dev/null
         find "$R/commit" -maxdepth 1 -name '*.json' -size -5M -exec cp {} "$1/" \; 2>/dev/null; cp "$R/commit.log" "$1/" 2>/dev/null; }
rm -rf "$R"
GUARDED_MAX_TAP=0 verity-vllm row run "$ROW" "$ROLE" "$REPO" "$REV" --stages build,match,commit > "$OUT/row_off.log" 2>&1; echo "row off rc $? $(date -u +%FT%TZ)"
keep "$OUT/evidence/off"; tail -n 4 "$R/stages.txt"
for s in 0 1; do
  rm -f "$R"/commit/dump_step*
  COMMIT_ARGS="--tensor-digests" VERITY_DUMP_STEP=$s GUARDED_MAX_TAP=1 verity-vllm row run "$ROW" "$ROLE" "$REPO" "$REV" --stages commit \
    > "$OUT/row_on$s.log" 2>&1; echo "row on (dump step $s) rc $? $(date -u +%FT%TZ)"; tail -n 3 "$R/stages.txt"
  mkdir -p "$OUT/evidence/on$s"; keep "$OUT/evidence/on$s"; cp "$R"/manifest.guarded-max-*.json "$OUT/evidence/on$s/" 2>/dev/null
  cp "$R"/commit/dump_step${s}_pair0_fa2.m1_L0_g*.bin "$R"/commit/dump_step${s}_pair0_layout.json "$OUT/evidence/on$s/" 2>/dev/null
done
python - "$OUT/evidence" <<'PY'
import glob, json, re, sys
import numpy as np
from verity_vllm.commit.hidden_stream import StreamLayout
from verity_vllm.properties import fa_tap_exactness as X
ev = sys.argv[1]
ROOT = "7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5"
KNOWN = {"368283add1a118085b88e62059d5f87f65c3d91b48265d217612e0ed726e9ff2": "the handoff's 368283ad (the record's, predates the relayout)",
         "90f8186879d5035af027259151b4ac465bf6c3dcf08c1e6d62dab9b680bfeaac": "90f81868 (from-scratch Build before the epoch; #95's flag-off arm)",
         "ee65240e662ee5206effcf22d8b24a30120ac372f0cf58e75621d3b8476dc625": "ee65240e (the AmpereBF16TcDot16_v2 epoch)"}
out = {}
for arm in ("off", "on0", "on1"):
    try:
        v = json.load(open(f"{ev}/{arm}/verdict.json")); m = json.load(open(f"{ev}/{arm}/manifest.json"))
    except Exception as e:
        out[arm] = {"error": repr(e)}; continue
    fam = (m.get("query") or {}).get("attention_hidden_family")
    out[arm] = {"outcome": v.get("outcome"), "commit_pass": v.get("commit_pass"), "first_fail": v.get("first_fail_reason"), "program": v.get("program_digest"),
                "manifest": m.get("manifest_digest"), "run_roots": v.get("run_roots"), "identities": len(m.get("identities") or []),
                "stream": {r["op_path"] + "@" + str(r["step"]): [r["element_range"], r["geometry"]] for r in m.get("identities") or [] if r.get("family") == fam},
                "guarded_max": (m.get("query") or {}).get("guarded_max")}
off, on0, on1 = (out.get(k, {}) for k in ("off", "on0", "on1"))
res = {"off_manifest": off.get("manifest"), "off_manifest_is": KNOWN.get(off.get("manifest"), "none of the known digests"),
       "off_run_root_equals_record": bool(off.get("run_roots")) and all(r == ROOT for r in off["run_roots"]),
       "on_run_roots_differ_from_record": bool(on0.get("run_roots")) and all(r != ROOT for r in on0["run_roots"]),
       "on_runs_one_root": bool(on0.get("run_roots")) and on0.get("run_roots") == on1.get("run_roots"),
       "on_identities_equal_off": on0.get("identities") == off.get("identities"), "on_manifest_differs": on0.get("manifest") != off.get("manifest"),
       "max_scaled_words_policy": ((on0.get("guarded_max") or {}).get("max_scaled") or {}).get("words"),
       "guard_words_policy": (on0.get("guarded_max") or {}).get("words")}
# every stream identity lengthened by exactly its MS class, nothing else moved
grow, bad = 0, []
for k, (er, g) in (off.get("stream") or {}).items():
    er1, g1 = (on0.get("stream") or {}).get(k, (None, None))
    want = [0, er[1] + g["HB"] * g["M"] * g["NB"]]
    if er1 != want or not (g1 or {}).get("ms") or {kk: vv for kk, vv in (g1 or {}).items() if kk != "ms"} != g:
        bad.append(k)
    grow += g["HB"] * g["M"] * g["NB"]
res.update(stream_identities=len(off.get("stream") or {}), stream_identities_lengthened_by_ms=len(off.get("stream") or {}) - len(bad),
           ms_words_in_manifest=grow, stream_identity_problems=bad[:5])
sl2 = X.scale_log2_bits({"softcap": 0.0}, 64)
for s in (0, 1):
    files = []
    for f in sorted(glob.glob(f"{ev}/on{s}/dump_step{s}_pair0_fa2.m1_L0_g*.bin")):
        g = re.search(r"_g(\d+)x(\d+)x(\d+)(?:x(\d+)x(\d+))?\.bin$", f)
        HB, M, NB, BN, D = int(g[1]), int(g[2]), int(g[3]), int(g[4] or 128), int(g[5] or 64)
        L = StreamLayout(HB, M, NB, BN, D, ms=True)
        w = np.fromfile(f, dtype=np.uint32)
        # step 0: the causal prefill (sq = sk = M, kBlockM 64); step 1: the swapped GQA decode, every row visits all NB blocks
        rows = [(h, r, min(NB, -(-((r // 64 + 1) * 64) // BN)) if s == 0 else NB) for h in range(HB) for r in range(M)]
        single = sum(1 for h, r, nbm in rows for b in range(nbm) if (s == 0 and b == nbm - 1 and (r + 1) - b * BN == 1)
                     or (s == 1 and (257 - b * BN) == 1))
        files.append({"file": f.rsplit("/", 1)[-1], "geometry": [HB, M, NB, BN, D], "words": int(w.size), "layout_words": L.padded_words(),
                      "ms": X.check_ms(w, L, iter(rows), sl2), "row3": X.check_row3(w, L, iter(rows)), "single_visible_key_blocks": single})
    res[f"committed_step{s}_layer0"] = files or "no dump"
out["result"] = res
for arm in ("off", "on0", "on1"):
    out.get(arm, {}).pop("stream", None)
json.dump(out, open(f"{ev}/summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
PY
echo "MS-ROW101-DONE $(date -u +%FT%TZ)"
