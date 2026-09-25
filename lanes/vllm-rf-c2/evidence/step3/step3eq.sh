# Step 3 equality only (research run --cwd source): old (base tree /workspace/base) vs new (head core) evaluators.
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
OUT=${RESEARCH_RUN_DIR:-/workspace/c2-step3}
mkdir -p "$OUT"
cat .research-source.json 2>/dev/null
sha256sum "$OUT/inputs/"* 2>/dev/null
export C2_BASE=/workspace/base C2_NPROC=${C2_NPROC:-32}
python "$OUT/inputs/equality3.py" "$OUT/equality3-quick.json" --quick > "$OUT/equality3-quick.log" 2>&1
rc4=$?
tail -5 "$OUT/equality3-quick.log"
if [ $rc4 -eq 1 ]; then echo "quick equality crashed"; tail -40 "$OUT/equality3-quick.log"; exit 1; fi
python "$OUT/inputs/equality3.py" "$OUT/equality3.json" > "$OUT/equality3.log" 2>&1
rc5=$?
grep -v '^ ' "$OUT/equality3.log" | tail -60
echo "equality-quick rc=$rc4 equality rc=$rc5"
exit $rc5
