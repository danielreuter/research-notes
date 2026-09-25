#!/bin/bash
# cpu pod, one research run from the shipped head tree ($PWD): bootstrap + a1's pins; head tree = a copy of it, base
# tree = a copy with the reverse patch `git diff --binary <head> <base>` applied; lints at both, core at head, then
# gate (b) (xdist -n 12 --dist loadfile, OMP_NUM_THREADS=3) at head and base side by side.
#   usage: research run --on vyv-rf-c4ir-cpu --source <head worktree> --cwd source --send cpu_gate_b.sh --send to_base.patch -- bash <path>
S=$PWD; L=$RESEARCH_RUN_DIR; H=/workspace/c4ir-head; B=/workspace/c4ir-base
echo "start $(date -u +%FT%TZ) src $S"
(cd $S/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap) > $L/bootstrap.log 2>&1
echo "bootstrap rc=$? $(date -u +%FT%TZ)"
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 xgrammar==0.2.7 >> $L/bootstrap.log 2>&1
echo "pins rc=$? $(date -u +%FT%TZ)"
uv pip freeze --python /workspace/venv312/bin/python > $L/freeze.txt 2>&1

for T in $H $B; do rm -rf $T && cp -a $S $T && find $T -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null; done
(cd $B && git apply -p1 $L/inputs/to_base.patch); echo "apply rc=$?"
[ -f $B/integrations/vllm/verity_vllm/query/boundary.py ] && [ ! -f $B/packages/verity/src/verity/ir/boundary.py ] \
  && [ ! -f $H/integrations/vllm/verity_vllm/query/boundary.py ] && [ -f $H/packages/verity/src/verity/ir/boundary.py ] && echo "tree shapes ok"

export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
pp() { echo "$1/integrations/vllm:$1/packages/verity/src:$1/tools/research/src"; }

for side in head base; do T=$H; [ $side = base ] && T=$B
  (cd $T && PYTHONPATH=$(pp $T) python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py \
     integrations/vllm/tests/test_imports_resolve.py -q -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/lints-$side.xml > $L/lints-$side.log 2>&1)
  echo "lints $side rc=$? $(date -u +%FT%TZ)"
done
(cd $H && PYTHONPATH=$H/packages/verity/src python -m pytest packages/verity/tests -ra -q -p no:cacheprovider \
   -o junit_family=xunit1 --junitxml=$L/core-head.xml > $L/core-head.log 2>&1)
echo "core head rc=$? $(date -u +%FT%TZ)"

env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|MKL_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/gate_b.env
for side in head base; do T=$H; [ $side = base ] && T=$B
  (cd $T && PYTHONPATH=$(pp $T) OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile \
     -o junit_family=xunit1 --junitxml=$L/gate_b-$side.xml > $L/gate_b-$side.log 2>&1; \
   echo "gate_b $side rc=$? $(date -u +%FT%TZ)") &
done
wait
echo "done $(date -u +%FT%TZ)"
