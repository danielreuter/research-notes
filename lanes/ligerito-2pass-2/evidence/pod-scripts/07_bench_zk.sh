# item 4 retry: 06_bench.sh's two --zk arms OOMed at the LGSC0004 11-coin opening fold (T (3,D,n0) 9 GiB; 6.8 GiB allocated,
# 8 GiB reserved-unallocated = fragmentation). Same runs with the allocator's expandable segments; non-ZK paired under it too.
source /workspace/env.sh; cd /workspace/src; B=/workspace/ligerito-2pass-2/bench; mkdir -p $B/oom-1; mv $B/local-zk* $B/live-zk* $B/oom-1/ 2>/dev/null
RV=/workspace/cargo-target/release/ligerito-verify; V=${V:-tcp://213.173.110.199:17864}
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True RESEARCH_GIT_COMMIT=$($PY -c "import json;print(json.load(open('/workspace/src/.research-source.json'))['commit'])")
run() { n=$1; shift; while [ -n "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]; do sleep 2; done
  $PY -m backends.direct.ligerito.run bench --relation fp8-ada --total-vus 4096 --reps 3 --dump-dir $B/$n --out $B/$n.json --rust-verifier $RV "$@" > $B/$n.log 2>&1; echo "$n exit $? (expandable_segments)" >> $B/summary.txt; }
run local-zk --coins local --zk
grep -q "local-zk exit 0" $B/summary.txt || { echo ZK_RETRY_FAILED >> $B/summary.txt; exit 1; }
run live-zk --coins live --zk --verifier $V
run local-nonzk-es --coins local
echo BENCH2_DONE >> $B/summary.txt
