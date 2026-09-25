#!/bin/bash
# vyv-rf-b5vab-reg: bootstrap, prefetch every fixture row with the minted read-only key (/root/r2ro.env, piped in from the
# VM), delete the key, then gate (a) T0+T1 at the shipped tree ($PWD) from the local store only.
#   usage: research run --on vyv-rf-b5vab-reg --project verity --custody-r2 --source <tree> --cwd source --timeout 21600
#          --send gate_a.sh -- bash -c 'bash "$RESEARCH_RUN_DIR/inputs/gate_a.sh"'
S=$PWD; L=$RESEARCH_RUN_DIR; H=/workspace/b5vab-gatea
echo "start $(date -u +%FT%TZ) src $S"
rm -rf $H && cp -a $S $H && find $H -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
if [ ! -x /workspace/venv312/bin/python ]; then
  (cd $H/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap) > $L/bootstrap.log 2>&1
  echo "bootstrap rc=$? $(tail -1 $L/bootstrap.log) $(date -u +%FT%TZ)"
  (export PATH=$HOME/.local/bin:/usr/local/bin:$PATH; uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0) >> $L/bootstrap.log 2>&1
fi
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$H/integrations/vllm:$H/packages/verity/src:$H/tools/research/src
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$H/tools/research/store.pod.toml
cd $H
for i in $(seq 1 120); do [ -s /root/r2ro.env ] && break; sleep 10; done
[ -s /root/r2ro.env ] || { echo "no key after 20 min $(date -u +%FT%TZ)"; exit 3; }
python - "$PWD" > $L/prefetch.txt <<'PY'
import sys, tomllib
f = tomllib.load(open(sys.argv[1] + "/integrations/vllm/tests/regression/fixtures.toml", "rb"))
for k, v in f.get("artifacts", {}).items():
    if v: print("top", k, v)
for rid, r in f["rows"].items():
    for k, v in r.get("artifacts", {}).items():
        if v: print(r.get("row", rid), k, v)
PY
( set -a; . /root/r2ro.env; set +a
  while read -r row kind art; do d=/workspace/prefetch/$row-$kind; rm -rf "$d"
    python -m research.cli data fetch "$art" --to "$d" > /dev/null 2>>$L/prefetch.err && echo "ok $row $kind" || echo "FAIL $row $kind"; rm -rf "$d"
  done < $L/prefetch.txt ) > $L/prefetch.log
rm -f /root/r2ro.env; unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN R2_ACCESS_KEY_ID R2_SECRET_ACCESS_KEY
echo "prefetch $(grep -c '^ok' $L/prefetch.log) ok, $(grep -c '^FAIL' $L/prefetch.log) FAIL; key deleted $(date -u +%FT%TZ) key_file_present=$([ -e /root/r2ro.env ] && echo yes || echo no)"
rm -rf /workspace/scratch/gate_a && mkdir -p /workspace/scratch/gate_a
export VERITY_REGRESSION_SCRATCH=/workspace/scratch/gate_a VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1
unset VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITY_REGRESSION_ENGINE VERITY_REGRESSION_ORACLE VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/gate_a.env
echo "gate_a start $(date -u +%FT%TZ)"
python -m pytest integrations/vllm/tests/regression -m regression -ra -o junit_family=xunit1 --junitxml=$L/gate_a.xml > $L/gate_a.log 2>&1
echo "gate_a rc=$? $(tail -1 $L/gate_a.log) $(date -u +%FT%TZ)"
