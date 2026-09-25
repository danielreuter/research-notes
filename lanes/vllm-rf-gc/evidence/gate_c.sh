#!/bin/bash
# lints + one test file at BASE and at the shipped sha, each in a git clone from the pod's bare repo (base must be an ancestor
# of the shipped sha, so the push carried it).  usage (research run --cwd source):
#   bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/gate_c.sh" <base sha> <test path>'   [--env BOOTSTRAP=1]
S=$PWD; L=$RESEARCH_RUN_DIR; W=/workspace/gc3; BASE=${1:?base}; TEST=${2:?test}; ROOT=/workspace/research
mkdir -p $W; export PATH=$HOME/.local/bin:$PATH
if [ "$BOOTSTRAP" = 1 ]; then
  (cd $S/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap) > $L/bootstrap.log 2>&1
  echo "bootstrap rc=$? $(date -u +%FT%TZ) $(tail -1 $L/bootstrap.log)"
  uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 >> $L/bootstrap.log 2>&1; echo "pins rc=$?"
fi
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO HARDEN_LIVE
for side in base:$BASE head:$RESEARCH_SOURCE_SHA; do
  TAG=${side%%:*}; SHA=${side#*:}; T=$W/$TAG; rm -rf $T
  git clone -q --no-checkout $ROOT/git/verity.git $T && git -C $T checkout -q --detach "$SHA" || { echo "CLONE-FAIL $SHA"; exit 3; }
  export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
  python -c "import verity_sampled_proofs" && echo "$TAG $SHA sampled_proofs ok"
  (cd $T && python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
     -q -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/lints-$TAG.xml > $L/lints-$TAG.log 2>&1)
  echo "lints $TAG rc=$? $(tail -1 $L/lints-$TAG.log)"
  (cd $T && HARDEN_OUT=$L/harden-$TAG python -m pytest $TEST -rA -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/test-$TAG.xml \
     > $L/test-$TAG.log 2>&1)
  echo "test $TAG rc=$? $(tail -1 $L/test-$TAG.log)"
done
echo "done $(date -u +%FT%TZ)"
