#!/bin/bash
# re-run at the shipped head (venv from r20260926-133406-4d7c): lints + the admission / placeholder tests, git clone, sampled_proofs on PYTHONPATH
S=$PWD; L=$RESEARCH_RUN_DIR; T=/workspace/mem/head3; rm -rf $T
git clone -q --no-checkout /workspace/research/git/verity.git $T && git -C $T checkout -q --detach $RESEARCH_SOURCE_SHA || exit 3
echo "clone vs shipped: $(diff -rq -x .git -x __pycache__ -x READY.json $S $T | wc -l) differing"
export PATH=/workspace/venv312/bin:$PATH CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
python -c "import verity_sampled_proofs" && echo "$(git -C $T rev-parse --short HEAD): verity_sampled_proofs importable"
(cd $T && python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q -p no:cacheprovider \
   > $L/lints.log 2>&1); echo "lints rc=$? $(tail -1 $L/lints.log)"
(cd $T && python -m pytest integrations/vllm/tests/commit/test_placeholder_steps.py integrations/vllm/tests/pipeline/test_admission_commit.py \
   integrations/vllm/tests/pipeline/test_admission_telemetry.py -q -p no:cacheprovider > $L/tests.log 2>&1); echo "tests rc=$? $(tail -1 $L/tests.log)"
