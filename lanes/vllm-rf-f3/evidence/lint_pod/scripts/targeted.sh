#!/bin/bash
# f3's own tests plus the tests of the code it touches (the earlier targeted list, less files main deleted), gate (b)'s environment.
#   usage: targeted.sh TREE TAG      logs: /workspace/rff3/logs/TAG.{log,xml}
T=$1; TAG=$2
L=/workspace/rff3/logs; mkdir -p $L
cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
V=integrations/vllm/tests
FILES=""
for f in acquire/test_plan.py acquire/test_p0_footprint.py acquire/test_fa2_tap_geometry.py acquire/test_native_collect.py \
  acquire/test_native_collect_flush.py acquire/test_native_collect_splits.py \
  check/test_challenge_seeds.py check/test_replay_synthetic.py check/test_sampled_replay.py check/test_compiled_linkage_attribution.py \
  commit/test_oracle.py commit/test_padding_steps.py \
  harness/test_run_config_dry_run.py harness/test_commit_delta_cli.py harness/test_commit_delta_placement_b1.py harness/test_compiled_merge_identity.py \
  observe/test_gen_llama.py observe/test_gen_ov_easy.py \
  program/test_compiled_replay_seed_source.py program/test_mufu_tables_pinned.py program/test_composition.py \
  program/test_sampling_rows.py program/test_sampling_operands.py program/test_derived_rows.py program/test_rmsnorm_fused.py \
  program/test_padding_pod_consumer.py program/test_lifted_tiny.py program/test_lifted_tiny_padrev.py \
  program/test_conformance_record.py program/test_derive_negative.py program/test_fp8.py \
  test_no_by_name_rules.py test_no_dead_modules.py; do
  if [ -f "$V/$f" ]; then FILES="$FILES $V/$f"; else echo "absent here: $f"; fi
done
echo "start $(date -u +%FT%TZ) tree $T sha $(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["commit"])' $T/.research-source.json 2>/dev/null)"
python -m pytest -ra -o junit_family=xunit1 --junitxml=$L/$TAG.xml $FILES > $L/$TAG.log 2>&1
rc=$?
echo "exit $rc $(date -u +%FT%TZ)"
echo "exit $rc $(date -u +%FT%TZ)" >> $L/$TAG.log
