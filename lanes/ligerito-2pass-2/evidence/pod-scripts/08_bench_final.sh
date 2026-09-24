# item 4 final: tree @ 0f6cc311 (bench contract fix), PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True for every arm
# (the --zk arms OOM without it: bench/oom-1). Earlier attempts kept: bench/local-nonzk (e0c7acd2, default allocator, passed),
# bench/attempt-2 (07: local-zk proved + Rust accepted but exit 1 on the contract's t.zk_additional rule).
source /workspace/env.sh; cd /workspace/src; B=/workspace/ligerito-2pass-2/bench; mkdir -p $B/attempt-2 $B/final
mv $B/local-zk* $B/attempt-2/ 2>/dev/null; B=$B/final
RV=/workspace/cargo-target/release/ligerito-verify; V=${V:-tcp://213.173.110.199:17864}
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True RESEARCH_GIT_COMMIT=$($PY -c "import json;print(json.load(open('/workspace/src/.research-source.json'))['commit'])")
run() { n=$1; shift; while [ -n "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]; do sleep 2; done
  $PY -m backends.direct.ligerito.run bench --relation fp8-ada --total-vus 4096 --reps 3 --dump-dir $B/$n --out $B/$n.json --rust-verifier $RV "$@" > $B/$n.log 2>&1; echo "$n exit $?" >> $B/summary.txt; }
nvidia-smi --query-gpu=name,clocks.sm,temperature.gpu --format=csv > $B/gpu.txt
run local-nonzk --coins local
run local-zk --coins local --zk
run live-zk --coins live --zk --verifier $V
echo BENCH_DONE >> $B/summary.txt
