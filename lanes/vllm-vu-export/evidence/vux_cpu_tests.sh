#!/usr/bin/env bash
# vux_cpu_tests.sh: CPU bootstrap, then the by-name / dead-module / ratchet lints and the exporter + program-graph tests
set -u
T=$PWD
cd integrations/vllm
bash verity_vllm/ops/pod_bootstrap.sh --cases B0 --out /workspace/vux/bootstrap-cpu --cpu > $RESEARCH_RUN_DIR/bootstrap.log 2>&1; echo "bootstrap rc $?"
export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
python -m pytest -q -p no:cacheprovider tests/test_no_by_name_rules.py tests/test_no_dead_modules.py tests/lint tests/pipeline/test_vu_export.py \
  tests/pipeline/test_program_graph.py tests/pipeline/test_cli.py -rfE 2>&1 | tail -15
