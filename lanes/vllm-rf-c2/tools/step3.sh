# Step 3 at the shipped head (research run --cwd source): lints, core ml tests, the registry tests touching the moved
# primitives, then old (base tree /workspace/base) vs new (head core) evaluator equality.
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
OUT=${RESEARCH_RUN_DIR:-/workspace/c2-step3}
mkdir -p "$OUT"
python -VV
cat .research-source.json 2>/dev/null
sha256sum "$OUT/inputs/"* 2>/dev/null
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
  -q -p no:cacheprovider --junitxml="$OUT/lints.xml"
rc1=$?
python -m pytest packages/verity/tests/ml -q -rfEs -p no:cacheprovider -n 8 --junitxml="$OUT/core-ml-tests.xml"
rc2=$?
T=integrations/vllm/tests
OMP_NUM_THREADS=2 python -m pytest $T/program/test_registry_one_process.py $T/program/test_fp8.py $T/program/test_derived_rows_fp8.py \
  $T/program/test_fp8_profile.py $T/program/test_pad_prims.py $T/program/test_moe_pad_route_a3.py $T/program/test_moe_pad_stage2.py \
  $T/program/test_lifted_moe.py $T/program/test_harden_moe.py $T/program/test_sampling_operands.py $T/program/test_sampling_rows.py \
  $T/program/test_sampling_policy.py $T/program/test_topp_splits_operand.py $T/program/test_ref_prims.py $T/program/test_lifted_tiny.py \
  $T/program/test_lifted_tiny_padrev.py $T/program/test_lifted_r17.py $T/program/test_frontend_analyses.py $T/program/test_derived_rows.py \
  $T/program/test_nan_conversion.py $T/program/test_codec.py $T/program/test_spec.py $T/program/test_serve3.py \
  $T/program/test_serve3_authored.py $T/program/test_twins.py $T/program/test_vllm_bindings_pins.py $T/program/test_mufu_tables_pinned.py \
  $T/check/test_sampled_replay.py $T/check/test_sampled_replay_stoch.py $T/observe/test_gen_sampling.py \
  $T/regression/test_step_segmentation.py $T/query/test_boundary_oracle.py ${EXTRA_TESTS:-} \
  -q -rfEs -p no:cacheprovider -n 12 --dist loadfile --junitxml="$OUT/registry-tests.xml"
rc3=$?
export C2_BASE=/workspace/base C2_NPROC=${C2_NPROC:-32}
python "$OUT/inputs/equality3.py" "$OUT/equality3-quick.json" --quick > "$OUT/equality3-quick.log" 2>&1
rc4=$?
tail -5 "$OUT/equality3-quick.log"
if [ $rc4 -eq 1 ]; then echo "quick equality crashed"; tail -40 "$OUT/equality3-quick.log"; rc5=1
else
  python "$OUT/inputs/equality3.py" "$OUT/equality3.json" 2>&1 | tee "$OUT/equality3.log" | grep -v '^ ' | tail -60
  rc5=${PIPESTATUS[0]}
fi
echo "lints rc=$rc1 core-ml rc=$rc2 registry-tests rc=$rc3 equality-quick rc=$rc4 equality rc=$rc5"
exit $(( rc1 | rc2 | rc3 | rc5 ))
