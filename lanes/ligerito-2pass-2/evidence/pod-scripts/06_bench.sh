# item 4: fp8-ada 4096 VUs, 1 batch, l 16384, RTX 4090, tree /workspace/src @ e0c7acd2 (11-coin default); one heavy job at a time
# local non-ZK, local ZK (--coins local: diagnostic), live ZK vs vy-ligerito-2pass-verifier (same DC EU-RO-1), each dumped + Rust
source /workspace/env.sh; cd /workspace/src; B=/workspace/ligerito-2pass-2/bench; mkdir -p $B
RV=/workspace/cargo-target/release/ligerito-verify; V=${V:-tcp://213.173.110.199:17864}
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 RESEARCH_GIT_COMMIT=$($PY -c "import json;print(json.load(open('/workspace/src/.research-source.json'))['commit'])")
while [ -n "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]; do sleep 5; done
nvidia-smi --query-gpu=name,clocks.sm,temperature.gpu --format=csv > $B/gpu.txt; cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us >> $B/gpu.txt
run() { n=$1; shift; while [ -n "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]; do sleep 2; done
  $PY -m backends.direct.ligerito.run bench --relation fp8-ada --total-vus 4096 --reps 3 --dump-dir $B/$n --out $B/$n.json --rust-verifier $RV "$@" > $B/$n.log 2>&1; echo "$n exit $?" >> $B/summary.txt; }
run local-nonzk --coins local
run local-zk --coins local --zk
run live-zk --coins live --zk --verifier $V
echo BENCH_DONE >> $B/summary.txt
