#!/bin/bash
# vllm-rf-m32 confirming gate (a) on main (copied from vllm-rf-c4ir/tools/reg_gate_a.sh; tree dir renamed). reg pod, one research run from the shipped head tree ($PWD): bootstrap + a1's pins, fixture prefetch with the
# read-only key in /root/r2ro.env (deleted on exit of the prefetch, never printed), then gate (a) T0+T1 on a copy.
#   usage: research run --on vyv-rf-c4ir-reg --source <head worktree> --cwd source --send reg_gate_a.sh -- bash <path>
S=$PWD; L=$RESEARCH_RUN_DIR; H=/workspace/m32-main
echo "start $(date -u +%FT%TZ) src $S"
(cd $S/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap) > $L/bootstrap.log 2>&1
echo "bootstrap rc=$? $(date -u +%FT%TZ)"
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 xgrammar==0.2.7 >> $L/bootstrap.log 2>&1
echo "pins rc=$? $(date -u +%FT%TZ)"
uv pip freeze --python /workspace/venv312/bin/python > $L/freeze.txt 2>&1

rm -rf $H && cp -a $S $H && find $H -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$H/integrations/vllm:$H/packages/verity/src:$H/tools/research/src
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$H/tools/research/store.pod.toml

(
  trap 'rm -f /root/r2ro.env' EXIT
  [ -s /root/r2ro.env ] || { echo "no key"; exit 5; }
  set -a; . /root/r2ro.env; set +a
  cd $H && python - "$H" > $L/prefetch.txt <<'PY'
import sys, tomllib
f = tomllib.load(open(sys.argv[1] + "/integrations/vllm/tests/regression/fixtures.toml", "rb"))
for k, v in f.get("artifacts", {}).items():
    if v: print("top", k, v)
for rid, r in f["rows"].items():
    for k, v in r.get("artifacts", {}).items():
        if v: print(r.get("row", rid), k, v)
PY
  while read -r row kind art; do d=/workspace/prefetch/$row-$kind; rm -rf "$d"
    python -m research.cli data fetch "$art" --to "$d" > /dev/null 2>> $L/prefetch.err && echo "ok $row $kind" || echo "FAIL $row $kind"; rm -rf "$d"
  done < $L/prefetch.txt > $L/prefetch.log
)
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "prefetch ok=$(grep -c '^ok' $L/prefetch.log) fail=$(grep -c '^FAIL' $L/prefetch.log) key_deleted=$([ -e /root/r2ro.env ] && echo no || echo yes) $(date -u +%FT%TZ)"
[ -e /root/r2ro.env ] && { echo "refusing: key still present"; exit 4; }

cd $H
mkdir -p /workspace/scratch/gate_a
export VERITY_REGRESSION_SCRATCH=/workspace/scratch/gate_a VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1
unset VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITY_REGRESSION_ENGINE VERITY_REGRESSION_ORACLE VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/gate_a.env
echo "gate_a start $(date -u +%FT%TZ)"
python -m pytest integrations/vllm/tests/regression -m regression -ra -o junit_family=xunit1 --junitxml=$L/gate_a.xml > $L/gate_a.log 2>&1
echo "gate_a rc=$? $(date -u +%FT%TZ)"
python3 $L/inputs/baseline-jdiff.py $L/inputs/gate_a-t0t1-base-72884c8a-samepod.xml.gz $L/gate_a.xml > $L/jdiff_gate_a.txt 2>&1
echo "jdiff vs a23b base rc=$?"; tail -8 $L/jdiff_gate_a.txt
echo "done $(date -u +%FT%TZ)"
