# gate (a): VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression,
# from the shipped source root (research run --cwd source), in venv312 (a23b's gate_a.sh; logs in the run dir).
# Runs from the local store only: every row's fixtures were prefetched and /root/r2ro.env deleted before this starts.
T=$PWD
OUT=${RESEARCH_RUN_DIR:-/workspace/c2/gate_a}; mkdir -p "$OUT" /workspace/c2/scratch-a
[ -e /root/r2ro.env ] && { echo "refusing: /root/r2ro.env present"; exit 4; }
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
export VERITY_REGRESSION_SCRATCH=/workspace/c2/scratch-a VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1
unset VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITY_REGRESSION_ENGINE VERITY_REGRESSION_ORACLE VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > "$OUT/gate_a.env"
cat .research-source.json 2>/dev/null
echo "start $(date -u +%FT%TZ) tree $T"
python -m pytest integrations/vllm/tests/regression -m regression -ra -o junit_family=xunit1 --junitxml="$OUT/gate_a.xml" > "$OUT/gate_a.log" 2>&1
rc=$?
tail -40 "$OUT/gate_a.log"
echo "exit $rc $(date -u +%FT%TZ)"
exit $rc
