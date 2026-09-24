#!/usr/bin/env bash
# timing A/B: bench_result on the dev tree with (default) or without (MODE=noomp) env.sh's thread caps.
# research run launches 04_record.sh without env.sh, so torch sizes its CPU pool to nproc (32) under a 13-core quota.
source /workspace/env.sh
MODE=${1:-noomp}
[ "$MODE" = noomp ] && unset OMP_NUM_THREADS MKL_NUM_THREADS OPENBLAS_NUM_THREADS VY_CPU_THREADS
O=/workspace/agkr-nvf4/prof-t$MODE; rm -rf $O; mkdir -p $O
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
$PY -m gpu.nvf4.circuit export --out $O/stmt > /dev/null
$PY -c "import torch; print('torch threads', torch.get_num_threads())"
RESEARCH_RUN_DIR=$O/run $PY bench_result.py $O/stmt --relation fp4-nvf4 --vus 4096 --reps 3 --warmup 1 \
    --verifier /workspace/bin/verity-gkr-verify --threads 13 > $O/prof.log 2>&1
echo "rc=$?"
grep -o -E '"(t_total|t_lookup|t_arith|t_open|t_open_acc|t_open_wq)": [0-9.]{1,6}' $O/prof.log | paste -sd' '
