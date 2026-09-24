#!/bin/bash
T=/workspace/tgt; L=/workspace/rff3/logs
cd $T || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
V=integrations/vllm/tests
python -m pytest -ra -o junit_family=xunit1 --junitxml=$L/targeted.xml \
  $V/acquire/test_plan.py $V/acquire/test_p0_footprint.py $V/acquire/test_fa2_tap_geometry.py $V/acquire/test_native_collect.py \
  $V/acquire/test_native_collect_flush.py $V/acquire/test_native_collect_splits.py \
  $V/check/test_challenge_seeds.py $V/check/test_replay_synthetic.py $V/check/test_sampled_replay.py $V/check/test_compiled_linkage_attribution.py \
  $V/commit/test_oracle.py $V/commit/test_padding_steps.py \
  $V/harness/test_run_config_dry_run.py $V/harness/test_commit_delta_cli.py $V/harness/test_commit_delta_placement_b1.py $V/harness/test_compiled_merge_identity.py \
  $V/program/test_compiled_replay_seed_source.py $V/program/test_mufu_tables_pinned.py $V/program/test_composition.py \
  $V/program/test_sampling_rows.py $V/program/test_sampling_operands.py $V/program/test_derived_rows.py $V/program/test_rmsnorm_fused.py \
  $V/program/test_padding_pod_consumer.py $V/program/test_lifted_tiny.py $V/program/test_lifted_tiny_padrev.py \
  $V/program/test_conformance_record.py $V/program/test_derive_negative.py $V/program/test_fp8.py \
  $V/test_no_by_name_rules.py $V/test_no_dead_modules.py > $L/targeted.log 2>&1
echo "exit $? $(date -u +%FT%TZ)" >> $L/targeted.log
