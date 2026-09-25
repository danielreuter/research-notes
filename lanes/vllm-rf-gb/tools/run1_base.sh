#!/bin/bash
# run 1 (cpu pod): bootstrap + the wave's pins, then lints and gate (b) at the shipped tree ($PWD = base 33e4d8d1).
#   usage: research run --on vyv-rf-gb-cpu --project verity --source <base worktree> --cwd source --custody-r2 \
#            --send run1_base.sh --send baseline-freeze.txt -- bash run1_base.sh
S=$PWD; L=$RESEARCH_RUN_DIR; W=/workspace/gb
mkdir -p $W
echo "start $(date -u +%FT%TZ) src $S"
(cd $S/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap) > $L/bootstrap.log 2>&1
echo "bootstrap rc=$? $(date -u +%FT%TZ) $(tail -1 $L/bootstrap.log)"
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 xgrammar==0.2.7 googleapis-common-protos==1.75.3 \
  uvicorn==0.53.0 >> $L/bootstrap.log 2>&1
echo "pins rc=$? $(date -u +%FT%TZ)"
uv pip freeze --python /workspace/venv312/bin/python > $L/freeze.txt 2>&1
diff $L/inputs/baseline-freeze.txt $L/freeze.txt > $L/freeze.diff && echo "freeze = a1's" || echo "freeze differs: $(wc -l < $L/freeze.diff) lines"
echo "$S" > $W/base-src.txt

T=$W/base; rm -rf $T && cp -a $S $T && find $T -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|MKL_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/gate_b.env
lscpu | grep -E 'Model name|^CPU\(s\)' > $L/host.txt; nproc >> $L/host.txt
cat /sys/fs/cgroup/memory.max >> $L/host.txt 2>/dev/null

(cd $T && python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py \
   integrations/vllm/tests/test_imports_resolve.py -q -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/lints-base.xml \
   > $L/lints-base.log 2>&1)
echo "lints base rc=$? $(date -u +%FT%TZ) $(tail -1 $L/lints-base.log)"
(cd $T && OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile \
   -o junit_family=xunit1 --junitxml=$L/gate_b-base.xml > $L/gate_b-base.log 2>&1)
echo "gate_b base rc=$? $(date -u +%FT%TZ) $(tail -1 $L/gate_b-base.log)"
cp $L/gate_b-base.xml $W/gate_b-base-run1.xml
echo "done $(date -u +%FT%TZ)"
