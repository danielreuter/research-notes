#!/usr/bin/env bash
# vux_graph4.sh: the branch's tests, then #4's program.json from the sweep of r20260926-000408-c3b4 (on this pod), into the run dir
set -u
T=$PWD; I=$RESEARCH_RUN_DIR/inputs
bash $I/vux_tests.sh
export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs VUX_REPO=$T/integrations/vllm
R=/workspace/research/runs/r20260926-000408-c3b4
python $I/program_graphs.py $RESEARCH_RUN_DIR/program-graphs smollm2-135m__bf16__l40s__tp1__b16__i1024__o128__mixed__greedy__bi-eager \
  /workspace/vux/sweep-4/smollm2-135m__bf16__l40s__tp1__b16__i1024__o128__mixed__greedy__bi-eager --record $R/evidence/sampled_replay_p0.json \
  --vus $R/vu-export/vus.jsonl --run r20260926-000408-c3b4 --row 4 --klass "PASS on run r20260926-000408-c3b4 (FAIL on the regression record)"
echo "GRAPH-DONE $(date -u +%FT%TZ)"
