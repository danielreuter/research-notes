#!/usr/bin/env bash
# sc_p4.sh: A4 run 1 (P4) on one L40S under research run --custody-r2: #101 with SERVING_ROWS=<partition file> (every layer-0 unit
# of the partition's four templates), then sc_members.py served: the served rows equal the captured instances in scope, and each
# member's m<k>-pub/inst equals M0's own write() (M0 at the tgz's commit).
# inputs (--send): the partition file, sc_members.py, m0-<sha>-py.tgz (M0's python, read-only), sets tgz (captured sets in member order)
set -u
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
T=$PWD; OUT=$RESEARCH_RUN_DIR; IN=$OUT/inputs; PF=$IN/${PARTITION_FILE:?}
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
bash verity_vllm/ops/pod_bootstrap.sh --cases B0,LLAMA32_1B --out /workspace/sc/bootstrap > "$OUT/bootstrap.log" 2>&1; echo "bootstrap rc $? $(date -u +%FT%TZ)"
export HIDDEN_SO=/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so PAIRS=1 VU_EXPORT=0 SERVING_ROWS=$PF SWEEP_DIR=/workspace/sc/sweep
rm -rf "$SWEEP_DIR/$ROW"
echo "row start $(date -u +%FT%TZ)"
verity-vllm row run "$ROW" LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da --stages build,match,commit \
  < /dev/null > "$OUT/row.log" 2>&1; echo "row rc $? $(date -u +%FT%TZ)"
R=$SWEEP_DIR/$ROW; mkdir -p "$OUT/evidence"; cp "$R/stages.txt" "$R/verdict.json" "$R/row.log" "$OUT/evidence/" 2>/dev/null
cat "$R/stages.txt" 2>/dev/null
python - "$R/verdict.json" <<'PY'
import json, sys
v = json.load(open(sys.argv[1])); print("verdict", v.get("outcome"), "program", v.get("program_digest"), "manifest", v.get("manifest_digest"), "roots", v.get("run_roots"))
PY
grep -rh "\[serving-rows\]" "$R" "$OUT/row.log" 2>/dev/null | tail -2
unset SERVING_ROWS
mkdir -p /workspace/sc/m0 /workspace/sc/sets && tar xzf "$IN"/m0-*-py.tgz -C /workspace/sc/m0 && tar xzf "$IN"/sets-*.tgz -C /workspace/sc/sets
WD=$OUT/serving-rows/$ROW; ls -la "$WD"; cat "$WD/error.txt" 2>/dev/null
PYTHONPATH=$PYTHONPATH:/workspace/sc/m0/backends/numerical/python:/workspace/sc/m0/backends/flock/python \
  python "$IN/sc_members.py" served "$WD" "$PF" "$OUT/m0-files" $SETS
cp "$OUT/m0-files/members.json" "$OUT/evidence/" 2>/dev/null
echo "SC-DONE $(date -u +%FT%TZ)"
