#!/usr/bin/env bash
# nonint_cli.sh TAG: non-interference through `verity-vllm noninterference` (a5's CLI) from the current tree
set -u
OUT=/workspace/b4c/$1; mkdir -p "$OUT"; cd integrations/vllm
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONPATH=$PWD:$PWD/../../packages/verity/src:$PWD/../../tools/research/src
python -m verity_vllm.pipeline.cli noninterference --workload workloads/workload_32x16_1req.json --out "$OUT/nonint" > "$OUT/nonint.log" 2>&1
echo "nonint rc $?" | tee -a "$OUT/rc.txt"; tail -n 3 "$OUT/nonint.log"
