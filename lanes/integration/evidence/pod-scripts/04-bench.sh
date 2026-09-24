#!/usr/bin/env bash
# integration merge-val-3 (d): one pipelined bench per relation family (--pipeline 4, zk interactive, local coins, 4096 VUs,
# l = 16384, --reps 3), rep1 dumped + pinned Rust batch beside it; then bench.summary over all
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
O=/workspace/integration/bench; mkdir -p $O
b() {  # tag, relation, extra args...
  local tag=$1 rel=$2; shift 2
  rm -rf $O/$tag; mkdir -p $O/$tag
  $PY -m backends.direct.ligero.run --relation $rel bench-vu --zk --mode interactive --batch 16384 --pipeline 4 \
      --total-vus 4096 --target -128 --reps 3 --dump-dir $O/$tag/proofs --dump-reps 1 --out $O/$tag/result.json "$@" \
      > $O/$tag/log 2>&1
  echo "$tag bench rc=$?" | tee -a $O/summary.txt
  local rep=$(ls -d $O/$tag/proofs/*/ 2>/dev/null | head -1)
  local hsys=""; [ -f $O/$tag/proofs/system_h.bin ] && hsys="--system-h $O/$tag/proofs/system_h.bin"
  $LIGERO_VERIFY batch --system $O/$tag/proofs/system.bin $hsys --dir ${rep:-$O/$tag/proofs} --target-bits 128 \
      > $O/$tag/proofs/rust_batch.json 2> $O/$tag/rust_batch.err
  echo "$tag rust rc=$? $(grep -o '"accepted":[0-9]*,"rejected":[0-9]*' $O/$tag/proofs/rust_batch.json | head -1) $(grep -o '"system_pinned":[a-z]*' $O/$tag/proofs/rust_batch.json | head -1)" | tee -a $O/summary.txt
}
b fp8-ada-bare fp8-ada
b bf16-hopper-bare bf16-hopper
b fp8-ada-shared fp8-ada --auth included-hash-shared --tile 64x64
$PY -m verity_numerical.bench.summary $O > $O/summary_table.txt 2>&1
$PY -m verity_numerical.bench.summary $O --json > $O/summary_table.json 2>&1
cat $O/summary_table.txt >> $O/summary.txt
echo BENCH_DONE | tee -a $O/summary.txt
