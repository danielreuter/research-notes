#!/usr/bin/env bash
# g1.sh TAG: #101 (FA2 matReq tap) build,match,commit PAIRS=1, then non-interference, from the current tree (research run --cwd source)
set -u
TAG=$1; OUT=/workspace/b4c/$TAG; mkdir -p "$OUT"
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
cd integrations/vllm
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
bash verity_vllm/ops/pod_bootstrap.sh --cases B0,LLAMA32_1B --out "$OUT/bootstrap" > "$OUT/bootstrap.log" 2>&1; echo "bootstrap rc $?" | tee -a "$OUT/rc.txt"
export HIDDEN_SO=/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so SWEEP_DIR=$OUT/sweep
PAIRS=1 bash verity_vllm/ops/row_pod.sh "$ROW" LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da build,match,commit \
  > "$OUT/row.log" 2>&1; echo "row rc $?" | tee -a "$OUT/rc.txt"
cat "$OUT/sweep/$ROW/stages.txt"
python -m verity_vllm.properties.noninterference --workload workloads/workload_32x16_1req.json --out "$OUT/nonint" \
  > "$OUT/nonint.log" 2>&1; echo "nonint rc $?" | tee -a "$OUT/rc.txt"
tail -n 5 "$OUT/nonint.log"
exit 0
