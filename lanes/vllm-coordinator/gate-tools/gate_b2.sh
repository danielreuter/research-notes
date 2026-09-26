#!/bin/bash
# gate (b) + lints in a GIT CHECKOUT of the shipped commit, on a vyv- cpu pod.
#   usage: research run --on <pod> --project verity --source <worktree> --cwd source --custody-r2 --send gate_b2.sh \
#            [--env BOOTSTRAP=1] [--env WAIT_RUN=<run dir>] -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/gate_b2.sh" <label>'
# The shipped tree ($PWD) has no .git; the tree under test is a clone of $RESEARCH_SOURCE_SHA from the pod's bare repo
# (<root>/git/verity.git, fed by research run's git transport), checked to hold the same files as the shipped tree (less the READY.json research adds).
S=$PWD; L=$RESEARCH_RUN_DIR; W=/workspace/gc2; TAG=${1:?label}; ROOT=/workspace/research
mkdir -p $W
if [ -n "$WAIT_RUN" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
export PATH=$HOME/.local/bin:$PATH
if [ "$BOOTSTRAP" = 1 ]; then
  (cd $S/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap) > $L/bootstrap.log 2>&1
  echo "bootstrap rc=$? $(date -u +%FT%TZ) $(tail -1 $L/bootstrap.log)"
  uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 xgrammar==0.2.7 googleapis-common-protos==1.75.3 \
    uvicorn==0.53.0 >> $L/bootstrap.log 2>&1
  echo "pins rc=$? $(date -u +%FT%TZ)"
fi
uv pip freeze --python /workspace/venv312/bin/python > $L/freeze.txt 2>&1
T=$W/$TAG; rm -rf $T
git clone -q --no-checkout $ROOT/git/verity.git $T && git -C $T checkout -q --detach "$RESEARCH_SOURCE_SHA" || { echo "CLONE-FAIL $RESEARCH_SOURCE_SHA"; exit 3; }
d=$(diff -rq -x .git -x __pycache__ -x READY.json $S $T | wc -l); echo "tree $T @ $(git -C $T rev-parse HEAD) vs shipped: $d differing entries"
[ "$d" = 0 ] || { diff -rq -x .git -x __pycache__ -x READY.json $S $T | head -20; exit 4; }
echo "start $(date -u +%FT%TZ) src $S tree $T"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
# protocols/sampled_proofs (PR #29) is a workspace member the bootstrap does not install yet
[ -d $T/protocols/sampled_proofs ] && export PYTHONPATH=$PYTHONPATH:$T/protocols/sampled_proofs
python -c "import verity_sampled_proofs" 2>/dev/null && echo "verity_sampled_proofs importable" || echo "verity_sampled_proofs NOT importable"
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|MKL_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/gate_b.env
(cd $T && python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py \
   integrations/vllm/tests/test_imports_resolve.py -q -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/lints-$TAG.xml \
   > $L/lints-$TAG.log 2>&1)
echo "lints $TAG rc=$? $(date -u +%FT%TZ) $(tail -1 $L/lints-$TAG.log)"
(cd $T && OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile \
   -o junit_family=xunit1 --junitxml=$L/gate_b-$TAG.xml > $L/gate_b-$TAG.log 2>&1)
echo "gate_b $TAG rc=$? $(date -u +%FT%TZ) $(tail -1 $L/gate_b-$TAG.log)"
cp $L/gate_b-$TAG.xml $W/gate_b-$TAG.xml
echo "done $(date -u +%FT%TZ)"
