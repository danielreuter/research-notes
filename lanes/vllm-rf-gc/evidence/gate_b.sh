#!/bin/bash
# gate (b) + lints at the shipped tree ($PWD), on a bootstrapped vyv- cpu pod (venv /workspace/venv312).
#   usage: research run --on vyv-rf-gb-cpu --project verity --source <worktree> --cwd source --custody-r2 \
#            --send gate_b.sh -- bash gate_b.sh <label>
S=$PWD; L=$RESEARCH_RUN_DIR; W=/workspace/gc; TAG=${1:?label}
mkdir -p $W
# WAIT_RUN=<run dir>: start only after that run left "running" (base and head never overlap on the pod)
if [ -n "$WAIT_RUN" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
T=$W/$TAG; rm -rf $T && cp -a $S $T && find $T -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
echo "start $(date -u +%FT%TZ) src $S tree $T"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
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
