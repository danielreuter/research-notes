#!/bin/bash
# vllm-rf-m32 bounded-finalize gate: bootstrap, git clone of the shipped sha (+ base 2ba5e62c from the same bare repo), sampled_proofs on
# PYTHONPATH; lints + targeted tests (admission, fork pool, the modules the change touches) at head, the targeted tests at base.
#   usage: research run --on <pod> --project verity --custody-r2 --source <head worktree> --cwd source --send mem_gate.sh -- bash -c 'bash $RESEARCH_RUN_DIR/inputs/mem_gate.sh'
S=$PWD; L=$RESEARCH_RUN_DIR; W=/workspace/mem; ROOT=/workspace/research; BASE=c20bab70; mkdir -p $W
export PATH=$HOME/.local/bin:$PATH CUDA_VISIBLE_DEVICES=-1
(cd $S/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap) > $L/bootstrap.log 2>&1
echo "bootstrap rc=$? $(date -u +%FT%TZ) $(tail -1 $L/bootstrap.log)"
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 xgrammar==0.2.7 googleapis-common-protos==1.75.3 uvicorn==0.53.0 >> $L/bootstrap.log 2>&1
echo "pins rc=$?"
TARGETS="integrations/vllm/tests/commit integrations/vllm/tests/pipeline/test_admission_commit.py integrations/vllm/tests/pipeline/test_admission_telemetry.py
 integrations/vllm/tests/pipeline/test_admission_planner.py integrations/vllm/tests/pipeline/test_admit_r19_host_working_set.py"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
for TAG in head base; do
  T=$W/$TAG; rm -rf $T; git clone -q --no-checkout $ROOT/git/verity.git $T || { echo "CLONE-FAIL"; exit 3; }
  SHA=$([ $TAG = head ] && echo $RESEARCH_SOURCE_SHA || echo $BASE)
  git -C $T checkout -q --detach $SHA || { echo "CHECKOUT-FAIL $SHA"; continue; }
  [ $TAG = head ] && { d=$(diff -rq -x .git -x __pycache__ -x READY.json $S $T | wc -l); echo "head clone vs shipped: $d differing"; }
  export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
  python -c "import verity_sampled_proofs" && echo "$TAG @ $(git -C $T rev-parse --short HEAD): verity_sampled_proofs importable"
  env | sort | grep -E '^(PATH|PYTHON|HF_|CUDA|VERITY)' > $L/env-$TAG.txt
  if [ $TAG = head ]; then
    (cd $T && python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
       -q -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/lints-$TAG.xml > $L/lints-$TAG.log 2>&1)
    echo "lints $TAG rc=$? $(tail -1 $L/lints-$TAG.log)"
  fi
  T2=""; for t in $TARGETS; do [ -e $T/$t ] && T2="$T2 $t"; done
  (cd $T && OMP_NUM_THREADS=3 python -m pytest $T2 -ra -n 12 --dist loadfile -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/targeted-$TAG.xml > $L/targeted-$TAG.log 2>&1)
  echo "targeted $TAG rc=$? $(tail -1 $L/targeted-$TAG.log)"
done
echo "done $(date -u +%FT%TZ)"
