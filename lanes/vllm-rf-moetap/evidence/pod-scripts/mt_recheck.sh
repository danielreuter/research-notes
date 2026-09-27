#!/bin/bash
# mt_recheck.sh: lints + the tap tests in a git clone of $RESEARCH_SOURCE_SHA (the pod's bare repo), the shipped tree checked as gate_b2.sh does.
S=$PWD; L=$RESEARCH_RUN_DIR; T=/workspace/gc2/recheck-${RESEARCH_SOURCE_SHA:0:8}; rm -rf $T
git clone -q --no-checkout /workspace/research/git/verity.git $T && git -C $T checkout -q --detach "$RESEARCH_SOURCE_SHA" || { echo CLONE-FAIL; exit 3; }
d=$(diff -rq -x .git -x __pycache__ -x READY.json -x build $S $T | wc -l); echo "tree $T @ $(git -C $T rev-parse HEAD) vs shipped (build dirs excluded: the router run compiled program/kernels/cpp/build into the shared source dir): $d differing entries"; [ "$d" = 0 ] || exit 4
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd $T && python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q -p no:cacheprovider > $L/lints.log 2>&1; echo "lints rc=$? $(tail -1 $L/lints.log)"
cd $T && python -m pytest integrations/vllm/tests/properties integrations/vllm/tests/acquire integrations/vllm/tests/query/test_router_softmax.py integrations/vllm/tests/query/test_vocab_range.py integrations/vllm/tests/query/test_norm_scales.py integrations/vllm/tests/program/test_moe_router_ordered.py integrations/vllm/tests/test_no_dead_modules.py -q -p no:cacheprovider -n 8 > $L/tests.log 2>&1; echo "tests rc=$? $(tail -1 $L/tests.log)"
echo "done $(date -u +%FT%TZ)"
