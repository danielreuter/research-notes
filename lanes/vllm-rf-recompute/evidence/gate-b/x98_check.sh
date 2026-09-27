#!/bin/bash
# test_weight_only_once.py in a git clone of $RESEARCH_SOURCE_SHA with PR #98's query modules (d7f76916 vs fa662029) applied.
L=$RESEARCH_RUN_DIR; T=/workspace/gc2/gemma3x98; rm -rf $T
git clone -q --no-checkout /workspace/research/git/verity.git $T 2>/dev/null && git -C $T checkout -q --detach "$RESEARCH_SOURCE_SHA" || { echo CLONE-FAIL; exit 3; }
git -C $T apply $L/inputs/pr98-query-d7f76916.patch || { echo PATCH-FAIL; exit 4; }
echo "tree $T @ $(git -C $T rev-parse HEAD) + pr98 query patch: $(git -C $T status --short | tr '\n' ' ')"
export PATH=/workspace/venv312/bin:$PATH PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= \
  PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd $T/integrations/vllm && python -m pytest -v -p no:cacheprovider -p no:logging -o junit_family=xunit1 --junitxml=$L/weight_only_once-x98.xml \
  tests/program/test_weight_only_once.py > $L/weight_only_once-x98.log 2>&1; rc=$?
grep -E "PASSED|FAILED|SKIPPED|passed|failed" $L/weight_only_once-x98.log; echo "rc=$rc"; rm -rf $T; exit $rc
