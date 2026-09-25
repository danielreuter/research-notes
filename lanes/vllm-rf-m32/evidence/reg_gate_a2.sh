#!/bin/bash
# vllm-rf-m32 gate (a) T0+T1 restart on the reg pod: reg_gate_a.sh without bootstrap/prefetch (venv312 and all 26 rows' fixtures
# are already in /workspace/research/store from r20260925-224008-395b; no key on the pod), PYTHONPATH + protocols/sampled_proofs.
#   usage: research run --on vyv-rf-m32-reg --source <tree> --cwd source --custody-r2 --send reg_gate_a2.sh --send baseline-jdiff.py \
#            --send gate_a-t0t1-base-72884c8a-samepod.xml.gz -- bash -c 'bash $RESEARCH_RUN_DIR/inputs/reg_gate_a2.sh'
S=$PWD; L=$RESEARCH_RUN_DIR; H=/workspace/m32-main2
echo "start $(date -u +%FT%TZ) src $S"
[ -e /root/r2ro.env ] && { echo "refusing: /root/r2ro.env present"; exit 4; }
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
rm -rf $H && cp -a $S $H && find $H -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$H/integrations/vllm:$H/packages/verity/src:$H/tools/research/src:$H/protocols/sampled_proofs
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$H/tools/research/store.pod.toml
cd $H
python -c "import verity_sampled_proofs as m, verity_vllm.commit.challenge; print('import verity_sampled_proofs OK', m.__file__)" || exit 6
mkdir -p /workspace/scratch/gate_a2
export VERITY_REGRESSION_SCRATCH=/workspace/scratch/gate_a2 VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1
unset VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITY_REGRESSION_ENGINE VERITY_REGRESSION_ORACLE VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/gate_a.env
python -m pytest integrations/vllm/tests/regression -m regression --collect-only -q > $L/collect.log 2>&1
echo "collect rc=$? $(tail -1 $L/collect.log)"
echo "gate_a start $(date -u +%FT%TZ)"
python -m pytest integrations/vllm/tests/regression -m regression -ra -o junit_family=xunit1 --junitxml=$L/gate_a.xml > $L/gate_a.log 2>&1
echo "gate_a rc=$? $(date -u +%FT%TZ) $(tail -1 $L/gate_a.log)"
python3 $L/inputs/baseline-jdiff.py $L/inputs/gate_a-t0t1-base-72884c8a-samepod.xml.gz $L/gate_a.xml > $L/jdiff_gate_a.txt 2>&1
echo "jdiff vs a23b base rc=$?"; tail -8 $L/jdiff_gate_a.txt
echo "done $(date -u +%FT%TZ)"
