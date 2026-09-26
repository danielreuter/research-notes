#!/usr/bin/env bash
# vux_word101.sh N ROW ROLE REPO REV [CASES]: bootstrap, run the row Build -> Match -> Commit (PAIRS=1) exactly as of record, then
# check Q_word_v1{X=16,W=32} on the row's own Build (`verity-vllm manifest build --word-check 16/32`, non-strict report + strict exit)
# and rebuild the manifest with the check on: its manifest_digest must equal the Build's. Prints the verdict's program digest,
# manifest digest and run roots for comparison with the record.
set -u
N=$1; ROW=$2; ROLE=$3; REPO=$4; REV=$5; CASES=${6:-B0,$ROLE}
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
bash verity_vllm/ops/pod_bootstrap.sh --cases "$CASES" --out "/workspace/vux/bootstrap-$N" > "$OUT/bootstrap.log" 2>&1; echo "bootstrap rc $? $(date -u +%FT%TZ)"
export HIDDEN_SO=/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so SWEEP_DIR=/workspace/vux/sweep-$N PAIRS=1 VERITY_VU_EXPORT_DIR=$OUT/vu-export
mkdir -p "$VERITY_VU_EXPORT_DIR"
rm -rf "$SWEEP_DIR/$ROW"
verity-vllm row run "$ROW" "$ROLE" "$REPO" "$REV" --stages build,match,commit > "$OUT/row.log" 2>&1; echo "row rc $? $(date -u +%FT%TZ)"
R=$SWEEP_DIR/$ROW
cp "$R/stages.txt" "$R/verdict.json" "$R/manifest.json" "$OUT/evidence/" 2>/dev/null
cp "$R/commit/manifest_verify.json" "$OUT/evidence/" 2>/dev/null
cat "$R/stages.txt" 2>/dev/null
WL=workloads/$ROW.json
verity-vllm manifest build --program "$R/build_request" --workload "$WL" --word-check 16/32 --out "$OUT/evidence/manifest_word.json" \
  > "$OUT/evidence/manifest_word.log" 2>&1; echo "word-check manifest build rc $?"
tail -n 3 "$OUT/evidence/manifest_word.log"
python - "$R" "$WL" "$OUT/evidence" <<'PY'
import json, sys
from verity_vllm.correspondence.reader_for_query import Correspondence
from verity_vllm.pipeline import manifest as M
from verity_vllm.query.program_view import from_instances
from verity_vllm.query.required import request_manifest
R, wl, ev = sys.argv[1], sys.argv[2], sys.argv[3]
d = R + "/build_request"
P = from_instances(d + "/instances.json.gz")
res = json.load(open(d + "/result.json"))
corr = Correspondence.of(P, d, implementation_paths=Correspondence.implementation_paths_of(res))
r = request_manifest(P, corr, res, workload=json.load(open(wl)), program_dir=d)
chk = M.word_check(P, corr, r.required, "16/32", strict=False)
json.dump({k: v for k, v in chk.items() if k != "groups"} | {"groups": [{k: g[k] for k in ("where", "definition", "calls", "units", "gates", "committed_interior_words", "violations")} for g in chk["groups"]]},
          open(ev + "/word_check.json", "w"), indent=1)
print("WORD", chk["query"], "ok" if chk["ok"] else "VIOLATIONS", "calls", chk["calls"], "units", chk["units"], "gates", chk["gates"], "committed_interior", chk["committed_interior_words"])
for v in chk["violations"][:20]:
    print("  VIOL", v["definition"], v["class"], v["calls"], v.get("where", [])[:2], v.get("out_bits"))
v = json.load(open(R + "/verdict.json"))
man = json.load(open(R + "/manifest.json"))
try:
    mw = json.load(open(ev + "/manifest_word.json"))["manifest_digest"]
except Exception:
    mw = None
print("verdict", v.get("outcome"), "program", v.get("program_digest"), "manifest", man.get("manifest_digest"), "manifest_with_word_check", mw,
      "roots", v.get("run_roots"))
PY
echo "VUX-WORD-DONE $(date -u +%FT%TZ)"
