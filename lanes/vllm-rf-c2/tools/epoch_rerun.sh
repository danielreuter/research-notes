# The epoch tree: the files that failed in the first epoch suite run, then the golden corpus check of every entry
# (the values an integrator re-record would write; corpus.json is protected and not edited here).
# Run with --cwd at the synced tree and --send epoch_tests.sh --send epoch_rerun.sh.
OUT=${RESEARCH_RUN_DIR:-/workspace/c2/epoch_rerun}; mkdir -p "$OUT"
bash "$OUT/inputs/epoch_tests.sh" \
  integrations/vllm/tests/program/test_codec.py integrations/vllm/tests/program/test_derive.py \
  integrations/vllm/tests/program/test_moe_pad_route_a3.py integrations/vllm/tests/program/test_nan_conversion.py \
  integrations/vllm/tests/query/test_query_fixtures.py integrations/vllm/tests/properties/test_golden.py \
  -n 6 --dist loadfile
T=/workspace/c2/gb-epoch/epoch; cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=3
echo "start golden $(date -u +%FT%TZ)"
python -m verity_vllm.properties.golden --check --out "$OUT/golden-epoch.json" > "$OUT/golden-epoch.log" 2>&1
echo "golden rc=$? $(date -u +%FT%TZ)"
tail -4 "$OUT/golden-epoch.log"
exit 0
