#!/usr/bin/env bash
# gm_row101_dump.sh: #101's tap-on Commit again (GUARDED_MAX_TAP=1, over the Build and Match gm_row101.sh left), twice, with the Commit's
# diagnostic --tensor-digests (COMMIT_ARGS) and VERITY_DUMP_STEP = 0 (the prefill) / 1 (a decode step): the committed bytes of attention layer
# 0's stream at that step.  Checks ROW word 3 there (check_row3: the IR's GuardNegInfZero_v1 of word 0 after a row's first key block, 0 at the
# first), that word 2 is the kernel's visit index, and that the run root equals the first tap-on run's.  Evidence: $RESEARCH_RUN_DIR/evidence.
set -u
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager; ROLE=LLAMA32_1B; REPO=unsloth/Llama-3.2-1B
REV=9535bd9b1d1dea6acafbdc4813b728796aeb28da; ON_ROOT=ae21ed2ee7b365c8b2617cdadd84d7201ffc2524b249583c9f4a3a5dfd23308f
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
unset HIDDEN_SO
export SWEEP_DIR=/workspace/gm/sweep PAIRS=1 VU_EXPORT=0 NORM_TAP=0
R=$SWEEP_DIR/$ROW
for s in 0 1; do
  rm -f "$R"/commit/dump_step*
  COMMIT_ARGS="--tensor-digests" VERITY_DUMP_STEP=$s GUARDED_MAX_TAP=1 verity-vllm row run "$ROW" "$ROLE" "$REPO" "$REV" --stages commit \
    > "$OUT/row_on_dump$s.log" 2>&1; echo "dump step $s rc $? $(date -u +%FT%TZ)"; tail -n 1 "$R/stages.txt"
  mkdir -p "$OUT/evidence/dump$s"; cp "$R/verdict.json" "$R/stages.txt" "$OUT/evidence/dump$s/"
  cp "$R"/commit/dump_step${s}_pair0_fa2.m1_L0_g*.bin "$R"/commit/dump_step${s}_pair0_layout.json "$OUT/evidence/dump$s/" 2>/dev/null
done
python - "$OUT/evidence" "$ON_ROOT" <<'PY'
import glob, json, re, sys
import numpy as np
from verity_vllm.commit.hidden_stream import StreamLayout
from verity_vllm.properties import fa_tap_exactness as X
ev, on_root = sys.argv[1], sys.argv[2]
out = {}
for s in (0, 1):
    v = json.load(open(f"{ev}/dump{s}/verdict.json"))
    ent = {"run_roots": v.get("run_roots"), "root_equals_first_tap_on_run": v.get("run_roots") == [on_root], "files": []}
    for f in sorted(glob.glob(f"{ev}/dump{s}/dump_step{s}_pair0_fa2.m1_L0_g*.bin")):
        g = re.search(r"_g(\d+)x(\d+)x(\d+)(?:x(\d+)x(\d+))?\.bin$", f)
        HB, M, NB, BN, D = int(g[1]), int(g[2]), int(g[3]), int(g[4] or 128), int(g[5] or 64)
        L = StreamLayout(HB, M, NB, BN, D)
        w = np.fromfile(f, dtype=np.uint32)
        # step 0: the causal prefill (sq = sk = M, kBlockM 64); a decode step: the swapped GQA launch, every row visits all NB blocks
        rows = [(h, r, min(NB, -(-((r // 64 + 1) * 64) // BN)) if s == 0 else NB) for h in range(HB) for r in range(M)]
        chk = X.check_row3(w, L, iter(rows))
        Rw = X._row_plane(w, L)
        word2 = all(int(Rw[h, r, b, 2]) == nbm - 1 - b for h, r, nbm in rows for b in range(nbm))
        ent["files"].append({"file": f.rsplit("/", 1)[-1], "geometry": [HB, M, NB, BN, D], "words": int(w.size), "layout_words": L.padded_words(),
                             **chk, "word2_is_visit_index": word2})
    out[f"step{s}"] = ent
json.dump(out, open(f"{ev}/summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
PY
echo "GM-ROW101-DUMP-DONE $(date -u +%FT%TZ)"
