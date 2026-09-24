# live_session_gpu_test.py is a script (pytest collected only live_session_test.py: 5 passed); run it, non-ZK and --zk, @0f6cc311
source /workspace/env.sh; cd /workspace/src; O=/workspace/ligerito-2pass-2/tests
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
$PY -m backends.direct.ligerito.live_session_gpu_test --out $O/r37-nonzk > $O/r37-nonzk.log 2>&1; echo "r37 nonzk exit $?" >> $O/summary.txt
$PY -m backends.direct.ligerito.live_session_gpu_test --zk --out $O/r37-zk > $O/r37-zk.log 2>&1; echo "r37 zk exit $?" >> $O/summary.txt
