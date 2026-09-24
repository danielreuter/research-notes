#!/bin/bash
# Build A/B on one GPU host: rebuild_digest_gate re-derives rows #73 (Qwen3-4B, BF16) and #74 (Qwen3-4B-FP8) from their recorded
# build_<wrapper>/result.json with the base tree (72884c8a) and the head tree, each gate comparing program_digest with the record; then
# tree_diff.py diffs the base and head output trees field by field.   usage: rebuild_ab.sh      out: /workspace/out/rebuild/
set -u
O=/workspace/out/rebuild; mkdir -p $O
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1 VLLM_BATCH_INVARIANT=1 PATH=/workspace/venv312/bin:$PATH
for T in base head2; do
  export PYTHONPATH=/workspace/$T/integrations/vllm:/workspace/$T/packages/verity/src
  cd /workspace/$T/integrations/vllm || exit 3
  python -m verity_vllm.harness.rebuild_digest_gate --row-dir /workspace/rows/r73 --out $O/$T/r73 --wrappers step,request_LP10_T8 > $O/$T.r73.log 2>&1
  python -m verity_vllm.harness.rebuild_digest_gate --row-dir /workspace/rows/r74 --out $O/$T/r74 --wrappers step,request_LP73_T1 > $O/$T.r74.log 2>&1
done
for r in r73 r74; do python /workspace/rff24/tree_diff.py $O/base/$r $O/head2/$r --out $O/diff_$r.json > $O/diff_$r.txt 2>&1; done
echo "done $(date -u +%FT%TZ)" > $O/DONE
