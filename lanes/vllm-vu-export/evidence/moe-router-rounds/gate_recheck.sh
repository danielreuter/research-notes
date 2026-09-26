#!/bin/bash
# gate_recheck.sh LABEL: in a git clone of the shipped commit (gate_b2.sh's recipe, no bootstrap), the lints, the router tests and the
# tests that failed on head only in the full gate (b)
S=$PWD; L=$RESEARCH_RUN_DIR; W=/workspace/gc2; TAG=${1:?label}; ROOT=/workspace/research
T=$W/$TAG; rm -rf $T
git clone -q --no-checkout $ROOT/git/verity.git $T && git -C $T checkout -q --detach "$RESEARCH_SOURCE_SHA" || { echo "CLONE-FAIL"; exit 3; }
d=$(diff -rq -x .git -x __pycache__ -x READY.json $S $T | wc -l); echo "tree $T @ $(git -C $T rev-parse HEAD): $d differing entries"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd $T
python -m pytest -q -p no:cacheprovider integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
  > $L/lints.log 2>&1; echo "lints rc=$? $(tail -1 $L/lints.log)"
python -m pytest -q -p no:cacheprovider -rfE integrations/vllm/tests/program/test_moe_router_ordered.py integrations/vllm/tests/engine/test_gen_ov_moe_padded.py \
  integrations/vllm/tests/engine/test_profiles_generic.py integrations/vllm/tests/engine/test_gen_ov_moe.py integrations/vllm/tests/engine/test_gen_ov_moe_qwen3.py \
  > $L/targeted.log 2>&1; echo "targeted rc=$? $(tail -1 $L/targeted.log)"; grep -E "^(FAILED|ERROR)" $L/targeted.log | head
for i in 1 2 3; do python -m pytest -q -p no:cacheprovider integrations/vllm/tests/commit/test_roundtrip.py::test_transient_storage_is_released > $L/roundtrip-$i.log 2>&1; echo "roundtrip $i rc=$? $(tail -1 $L/roundtrip-$i.log)"; done
