#!/usr/bin/env bash
# One contract bench-result of the modified-SP1 (TC_DOT chip) variant on the A100: backends/sp1/tcdot/bench.py
# (= benchmarks/dot_product/vector_run.py --backend sp1-bare) over vu-k1536 [0, 4096) of bench-instances/v1.
# Env: TAG (run dir name), REPS (3), VPR (vus per read, 64), THRESH (vu_software_threshold, 8), NOTE, EXTRA (more args),
# SERVER_HOME (home-bf16 = fork fe35cc50's server; home-shard = d14b4c62's), ELEMENT_THRESHOLD (honoured from d14b4c62).
set -euo pipefail
W=/workspace/sp1-tcdot
S=$W/src
export PATH=$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH
# sp1-sdk's cuda client runs $HOME/.sp1/bin/sp1-gpu-server: the server built from the fork
export HOME=$W/${SERVER_HOME:-home-bf16}
export CUDA_VISIBLE_DEVICES=0
export RESEARCH_SOURCE_COMMIT=$(python3 -c "import json;d=json.load(open('$S/.research-source.json'));print(d['commit']+('+dirty' if d['dirty'] else ''))")
export VERITY_TCDOT_VU_SOFTWARE_THRESHOLD=${THRESH:-8}
TAG=${TAG:-bench-$(date -u +%Y%m%dT%H%MZ)}
export RESEARCH_RUN_ID=sp1-tcdot-$TAG
H=$W/target-tcdot/release/verity-tcdot-host
RUN=$W/runs/$TAG
mkdir -p $RUN
echo "source $RESEARCH_SOURCE_COMMIT host $(sha256sum $H | cut -c1-16) server $(sha256sum $HOME/.sp1/bin/sp1-gpu-server | cut -c1-16) threshold $VERITY_TCDOT_VU_SOFTWARE_THRESHOLD"
cd $S
python3 backends/sp1/tcdot/bench.py --host $H --instances $W/bi --reps ${REPS:-3} --warmup-vus 64 --vus-per-read ${VPR:-64} \
  --out $RUN --note "${NOTE:-}" ${EXTRA:-}
