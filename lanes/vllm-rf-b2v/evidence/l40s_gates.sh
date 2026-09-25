#!/bin/bash
# On vyv-rf-b2v-l40s after row #101: the lints and the lane's unit tests at the head, then gate (b) at the head and at the base side by
# side (separate trees).  usage: l40s_gates.sh      logs: /workspace/out/gates/*.{log,xml,env,status,rss}
H=/workspace/head; B=/workspace/base; L=/workspace/out/gates; mkdir -p $L
export PATH=$HOME/.local/bin:/workspace/venv312/bin:$PATH
/workspace/venv312/bin/python -c 'import xdist' 2>/dev/null || uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 > $L/xdist.log 2>&1
stamp() { echo "[l40s_gates] $(date -u +%FT%TZ) $*"; }
lint() {  # TREE TAG
  ( cd "$1" && export CUDA_VISIBLE_DEVICES="" PYTHONPATH=$1/integrations/vllm:$1/packages/verity/src:$1/tools/research/src HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1 &&
    python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q \
      -o junit_family=xunit1 --junitxml=$L/$2.xml > $L/$2.log 2>&1; echo "exit $? $(date -u +%FT%TZ)" >> $L/$2.log )
}
stamp "lints head"; lint $H lint_head; tail -3 $L/lint_head.log
stamp "unit tests head (check, commit, properties, observe ref integrity)"
( cd $H && export CUDA_VISIBLE_DEVICES="" PYTHONPATH=$H/integrations/vllm:$H/packages/verity/src:$H/tools/research/src HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1 &&
  OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests/check integrations/vllm/tests/commit integrations/vllm/tests/properties \
    integrations/vllm/tests/observe/test_ref_integrity.py -q -n 12 --dist loadfile -o junit_family=xunit1 --junitxml=$L/unit_head.xml > $L/unit_head.log 2>&1
  echo "exit $? $(date -u +%FT%TZ)" >> $L/unit_head.log )
tail -3 $L/unit_head.log
stamp "gate (b) head and base"
OMP_NUM_THREADS=3 bash /workspace/b2v/gate_b.sh $H b_head -n 12 --dist loadfile &
P1=$!
OMP_NUM_THREADS=3 bash /workspace/b2v/gate_b.sh $B b_base -n 12 --dist loadfile &
P2=$!
wait $P1; wait $P2
tail -2 $L/b_head.log $L/b_base.log
/workspace/venv312/bin/python /workspace/b2v/jdiff.py $L/b_base.xml $L/b_head.xml > $L/b_jdiff.txt 2>&1; echo "jdiff exit $?" >> $L/b_jdiff.txt
tail -40 $L/b_jdiff.txt
stamp done
