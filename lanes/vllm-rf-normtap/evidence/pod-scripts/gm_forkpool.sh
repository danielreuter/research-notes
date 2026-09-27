#!/usr/bin/env bash
# gm_forkpool.sh: tests/check/test_fork_pool.py five times in each gate (b) clone (base and head of gate_b3.sh, same pod, GPU hidden), to tell a
# timing failure from a regression.
set -u
OUT=$RESEARCH_RUN_DIR
export PATH=/workspace/venv312/bin:$PATH PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=""
for tag in base head; do
  T=/workspace/gc2/$tag
  export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
  for i in 1 2 3 4 5; do
    (cd $T && python -m pytest integrations/vllm/tests/check/test_fork_pool.py -q -p no:cacheprovider > $OUT/forkpool-$tag-$i.log 2>&1)
    echo "$tag run $i rc=$? $(tail -1 $OUT/forkpool-$tag-$i.log)"
  done
done
echo "GM-FORKPOOL-DONE $(date -u +%FT%TZ)"
