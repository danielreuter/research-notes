#!/bin/bash
# reg pod: (1) custody copy of the killed gate (a) run r20260925-120631-fb6b (SIGTERM at its 4 h stage timeout, 16:12Z,
# after 130 of 158 tests, no JUnit) into this run's dir; (2) gate (a) T0+T1 tests 131..158 (a23b base order) at the
# shipped head tree ($PWD), same env as reg_gate_a.sh, on the fixtures already in /workspace/research/store (no fetch).
#   usage: research run --on vyv-rf-c4ir-reg --project verity --custody-r2 --source <7313e799> --cwd source --timeout 7200
#          --send reg_gate_a_tail.sh --send tail_ids.txt -- bash <run dir>/inputs/reg_gate_a_tail.sh
S=$PWD; L=$RESEARCH_RUN_DIR; P=r20260925-120631-fb6b; H=/workspace/c4irc-gatea-tail
echo "start $(date -u +%FT%TZ) src $S"
[ -n "$SKIP_CUSTODY" ] || { mkdir -p $L/prior && cp -a /workspace/research/runs/$P $L/prior/ && (cd $L/prior/$P && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS)
echo "custody copy rc=$? files=$(find $L/prior/$P -type f | wc -l) bytes=$(du -sb $L/prior/$P | cut -f1) $(date -u +%FT%TZ)"; }

rm -rf $H && cp -a $S $H && find $H -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$H/integrations/vllm:$H/packages/verity/src:$H/tools/research/src
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$H/tools/research/store.pod.toml
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
cd $H
rm -rf /workspace/scratch/gate_a_tail && mkdir -p /workspace/scratch/gate_a_tail
export VERITY_REGRESSION_SCRATCH=/workspace/scratch/gate_a_tail VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1
unset VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITY_REGRESSION_ENGINE VERITY_REGRESSION_ORACLE VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/gate_a_tail.env
echo "gate_a_tail start $(date -u +%FT%TZ) ids=$(wc -l < $L/inputs/tail_ids.txt)"
set -f
python -m pytest -v $(sed 's#^#integrations/vllm/#' $L/inputs/tail_ids.txt) -m regression -ra -o junit_family=xunit1 --junitxml=$L/gate_a_tail.xml > $L/gate_a_tail.log 2>&1
echo "gate_a_tail rc=$? $(date -u +%FT%TZ)"
