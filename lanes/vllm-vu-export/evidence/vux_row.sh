#!/usr/bin/env bash
# vux_row.sh N ROW ROLE REPO REV [CASES]: bootstrap from the shipped tree, run the row Build -> Match -> Commit (PAIRS=1) with the
# VU export armed (--vu-export-dir via VERITY_VU_EXPORT_DIR), then verify the export.  The sets land in $RESEARCH_RUN_DIR/vu-export,
# so --custody-r2 preserves them with the run.  Optional LIMITS='{"per_family": ...}' (vu_export.Limits fields).
set -u
N=$1; ROW=$2; ROLE=$3; REPO=$4; REV=$5; CASES=${6:-B0,$ROLE}
T=$PWD; OUT=$RESEARCH_RUN_DIR; EXP=$OUT/vu-export; mkdir -p "$EXP"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
bash verity_vllm/ops/pod_bootstrap.sh --cases "$CASES" --out "/workspace/vux/bootstrap-$N" > "$OUT/bootstrap.log" 2>&1; echo "bootstrap rc $? $(date -u +%FT%TZ)"
# the tree: research run ships `git archive` of a clean commit (dirty trees are refused), so dirty = false; BRANCH / EPOCH from the caller
printf '{"row": %s, "row_key": "%s", "research_run": "%s", "source": {"commit": "%s", "dirty": false, "branch": "%s"}, "epoch": "%s"}\n' \
  "$N" "$ROW" "${RESEARCH_RUN_ID:-}" "${RESEARCH_SOURCE_SHA:-unknown}" "${BRANCH:-unknown}" "${EPOCH:-unknown}" > "$EXP/provenance.json"
[ -n "${LIMITS:-}" ] && printf '%s\n' "$LIMITS" > "$EXP/limits.json"
export HIDDEN_SO=/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so SWEEP_DIR=/workspace/vux/sweep-$N PAIRS=1 VERITY_VU_EXPORT_DIR=$EXP
rm -rf "$SWEEP_DIR/$ROW"
verity-vllm row run "$ROW" "$ROLE" "$REPO" "$REV" --stages build,match,commit > "$OUT/row.log" 2>&1; echo "row rc $? $(date -u +%FT%TZ)"
R=$SWEEP_DIR/$ROW; mkdir -p "$OUT/evidence"
cp "$R/stages.txt" "$R/verdict.json" "$R/row.log" "$OUT/evidence/" 2>/dev/null
cp "$R/commit/sampled_replay_p0.json" "$OUT/evidence/" 2>/dev/null
cat "$R/stages.txt" 2>/dev/null
grep -rh "\[vu-export\]" "$R" 2>/dev/null | tail -3
python - "$EXP" "$OUT/evidence/verdict.json" <<'PY'
import json, sys
from verity_vllm.pipeline import vu_export as V
exp, vpath = sys.argv[1], sys.argv[2]
try:
    v = json.load(open(vpath)); print("verdict", v.get("outcome"), "program", v.get("program_digest", "")[:16], "manifest", v.get("manifest_digest", "")[:16], "roots", [r[:16] for r in v.get("run_roots") or []])
except Exception as e:
    print("no verdict", e)
try:
    s = json.load(open(exp + "/export.json"))
except Exception as e:
    print("NO EXPORT", e); sys.exit(0)
for f, c in s["by_family"].items():
    print("family", f, json.dumps(c))
for x in s["sets"]:
    print("set", x["set"], x["n"], x["bytes"], x["content_digest"][:16])
r = V.verify(exp)
json.dump(r, open(exp + "/verify.json", "w"), indent=1)
print("VERIFY", "OK" if r["ok"] else "FAIL", [(x["set"], x["n"], x.get("bad_n")) for x in r["sets"] if not x["ok"]])
PY
echo "VUX-DONE $(date -u +%FT%TZ)"
