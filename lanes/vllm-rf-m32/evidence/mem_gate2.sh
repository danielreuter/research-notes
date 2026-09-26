#!/bin/bash
# re-run of the fork-pool and admission tests at the shipped head (venv from r20260926-082110-dc3a), in a git clone, sampled_proofs on PYTHONPATH
S=$PWD; L=$RESEARCH_RUN_DIR; T=/workspace/mem/head2; rm -rf $T
git clone -q --no-checkout /workspace/research/git/verity.git $T && git -C $T checkout -q --detach $RESEARCH_SOURCE_SHA || exit 3
echo "clone vs shipped: $(diff -rq -x .git -x __pycache__ -x READY.json $S $T | wc -l) differing"
export PATH=/workspace/venv312/bin:$PATH CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
python -c "import verity_sampled_proofs" && echo "$(git -C $T rev-parse --short HEAD): verity_sampled_proofs importable"
(cd $T && python -m pytest integrations/vllm/tests/check/test_fork_pool.py integrations/vllm/tests/pipeline/test_admission_commit.py -v -p no:cacheprovider \
   -o junit_family=xunit1 --junitxml=$L/tests-head2.xml > $L/tests-head2.log 2>&1); echo "tests rc=$? $(tail -1 $L/tests-head2.log)"
grep -E "PASSED|FAILED|ERROR" $L/tests-head2.log | sed 's/ *\[.*//'
