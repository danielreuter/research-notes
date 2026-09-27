#!/usr/bin/env bash
# sc_gpu.sh: the serving-commit GPU check on one L40S, under one `research run --custody-r2` of lane/vllm-serving-commit.
#   A: #101 row, SERVING_ROWS unset (the default path: program ccc21347, manifest 90f81868, run root 7adcef49, verdict PASS)
#   B: #101 row, SERVING_ROWS=<partition-183680.json> (the vllm-v1 root unchanged; every RoPE head committed in M0's format)
#   C: sc_compare.py on B's window (captured heads equal, M0's write() equal, the agreed circuit pin, overhead)
# inputs (--send): partition-183680.json, m0-e51e2b86-py.tgz (M0's python at e51e2b86, read-only), ropeset.tgz (art:16825154),
#                  sc_compare.py.  Everything lands in $RESEARCH_RUN_DIR, which custody preserves.
set -u
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
T=$PWD; OUT=$RESEARCH_RUN_DIR; IN=$OUT/inputs
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
bash verity_vllm/ops/pod_bootstrap.sh --cases B0,LLAMA32_1B --out /workspace/sc/bootstrap > "$OUT/bootstrap.log" 2>&1; echo "bootstrap rc $? $(date -u +%FT%TZ)"
python -c "import verity_sampled_proofs; print('verity_sampled_proofs ok')"
export HIDDEN_SO=/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so PAIRS=1 VU_EXPORT=0
verdict() { python - "$1" <<'PY'
import json, sys
v = json.load(open(sys.argv[1]))
print("verdict", v.get("outcome"), "program", v.get("program_digest", ""), "manifest", v.get("manifest_digest", ""), "roots", v.get("run_roots"))
PY
}
for MODE in ${MODES:-off on}; do
  export SWEEP_DIR=/workspace/sc/sweep-$MODE
  rm -rf "$SWEEP_DIR/$ROW"
  if [ $MODE = on ]; then export SERVING_ROWS=$IN/${PARTITION_FILE:-partition-183680.json}; else unset SERVING_ROWS; fi
  echo "row $MODE start $(date -u +%FT%TZ)"
  verity-vllm row run "$ROW" LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da --stages build,match,commit \
    < /dev/null > "$OUT/row-$MODE.log" 2>&1; echo "row $MODE rc $? $(date -u +%FT%TZ)"
  R=$SWEEP_DIR/$ROW; mkdir -p "$OUT/evidence/$MODE"
  cp "$R/stages.txt" "$R/verdict.json" "$R/row.log" "$OUT/evidence/$MODE/" 2>/dev/null
  cat "$R/stages.txt" 2>/dev/null; verdict "$R/verdict.json"
  grep -rh "\[serving-rows\]" "$R" "$OUT/row-$MODE.log" 2>/dev/null | tail -2
done
unset SERVING_ROWS
mkdir -p /workspace/sc/m0 && tar xzf "$IN/m0-e51e2b86-py.tgz" -C /workspace/sc/m0 && tar xzf "$IN/ropeset.tgz" -C /workspace/sc
WD=$OUT/serving-rows/$ROW
ls -la "$WD" 2>&1; cat "$WD/error.txt" 2>/dev/null
PYTHONPATH=$PYTHONPATH:/workspace/sc/m0/backends/numerical/python:/workspace/sc/m0/backends/flock/python \
  python "$IN/sc_compare.py" "$WD" /workspace/sc/ropeset "$IN/${PARTITION_FILE:-partition-183680.json}" "$OUT/m0-files" "$OUT/evidence/on/stages.txt"
echo "SC-DONE $(date -u +%FT%TZ)"
