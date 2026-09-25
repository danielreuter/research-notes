#!/bin/bash
# vllm-rf-m32 gates on a fresh cpu3g pod, from the head tree ($PWD): bootstrap (a1's pins), targeted tests at head,
# then lints + gate (b) at base (head with to_base.patch reversed-in) and head, sequentially on this pod, and jdiff.
#   usage: research run --on vyv-rf-m32-cpu --project verity --source <head worktree> --cwd source --custody-r2 \
#            --send m32_gates.sh --send to_base.patch --send baseline-jdiff.py -- bash m32_gates.sh
S=$PWD; L=$RESEARCH_RUN_DIR; W=/workspace/m32; I=$L/inputs; mkdir -p $W
echo "start $(date -u +%FT%TZ) src $S"
(cd $S/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap) > $L/bootstrap.log 2>&1
echo "bootstrap rc=$? $(date -u +%FT%TZ) $(tail -1 $L/bootstrap.log)"
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 xgrammar==0.2.7 googleapis-common-protos==1.75.3 \
  uvicorn==0.53.0 >> $L/bootstrap.log 2>&1
echo "pins rc=$? $(date -u +%FT%TZ)"
uv pip freeze --python /workspace/venv312/bin/python > $L/freeze.txt 2>&1
for TAG in head base; do T=$W/$TAG; rm -rf $T && cp -a $S $T && find $T -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null; done
(cd $W/base && patch -p1 < $I/to_base.patch > $L/patch.log 2>&1); echo "base patch rc=$?"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
lscpu | grep -E 'Model name|^CPU\(s\)' > $L/host.txt; nproc >> $L/host.txt
run() {  # TAG
  local T=$W/$1; export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
  env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|VERITY|VERITOR|RESEARCH)' > $L/gate_b-$1.env
  (cd $T && python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py \
     integrations/vllm/tests/test_imports_resolve.py -q -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/lints-$1.xml > $L/lints-$1.log 2>&1)
  echo "lints $1 rc=$? $(date -u +%FT%TZ) $(tail -1 $L/lints-$1.log)"
  (cd $T && OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile -p no:cacheprovider \
     -o junit_family=xunit1 --junitxml=$L/gate_b-$1.xml > $L/gate_b-$1.log 2>&1)
  echo "gate_b $1 rc=$? $(date -u +%FT%TZ) $(tail -1 $L/gate_b-$1.log)"
}
T=$W/head; export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
(cd $T && python -m pytest integrations/vllm/tests/commit packages/verity/tests/commitments -q -p no:cacheprovider -n 12 \
   -o junit_family=xunit1 --junitxml=$L/targeted-head.xml > $L/targeted-head.log 2>&1)
echo "targeted head rc=$? $(date -u +%FT%TZ) $(tail -1 $L/targeted-head.log)"
(cd $T && python -m pytest integrations/vllm/tests/commit/test_production_vectors.py -q -p no:cacheprovider -k "chunk_header" > $L/new-tests.log 2>&1)
echo "new tests rc=$? $(tail -1 $L/new-tests.log)"
run base; run head
python3 $I/baseline-jdiff.py $L/gate_b-base.xml $L/gate_b-head.xml > $L/jdiff.txt 2>&1; echo "jdiff rc=$?"; tail -5 $L/jdiff.txt
echo "done $(date -u +%FT%TZ)"
