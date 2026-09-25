# gate (b) at the shipped head and at the base tree, side by side on this pod (research run --cwd source):
#   OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile
# Each side runs in its own fresh copy (the suites write under the tree); __pycache__ and build dirs are not copied.
OUT=${RESEARCH_RUN_DIR:-/workspace/c2/gate_b}; mkdir -p "$OUT"
BASE_SRC=${C2_BASE:-/workspace/base}
W=/workspace/c2/gb; rm -rf $W; mkdir -p $W
cp -a "$PWD" $W/head && cp -a "$BASE_SRC" $W/base
find $W -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
cat .research-source.json 2>/dev/null
side() {  # side NAME
  local T=$W/$1
  ( cd "$T" || exit 3
    export PATH=/workspace/venv312/bin:$PATH
    export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
    export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=3
    unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
    env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|MKL_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > "$OUT/gate_b-$1.env"
    echo "start $1 $(date -u +%FT%TZ)"
    python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile -o junit_family=xunit1 --junitxml="$OUT/gate_b-$1.xml" \
      > "$OUT/gate_b-$1.log" 2>&1
    rc=$?; echo "exit $1 $rc $(date -u +%FT%TZ)"; exit $rc )
}
( while sleep 20; do echo "$(date -u +%FT%TZ) $(cat /sys/fs/cgroup/memory.current 2>/dev/null)"; done ) > "$OUT/gate_b.mem" 2>&1 &
MON=$!
side head & P1=$!
side base & P2=$!
wait $P1; r1=$?; wait $P2; r2=$?
kill $MON 2>/dev/null
for s in head base; do tail -3 "$OUT/gate_b-$s.log"; done
echo "gate_b head rc=$r1 base rc=$r2"
exit 0
