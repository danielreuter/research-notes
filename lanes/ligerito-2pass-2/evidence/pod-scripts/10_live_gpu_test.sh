# R3-7 end to end on the GPU at 0f6cc311 (complements redteam_live_labels.py, item 5): loopback live.Server, real proofs on each attack's slots
source /workspace/env.sh; cd /workspace/src; O=/workspace/ligerito-2pass-2/tests; mkdir -p $O
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
timeout 1500 $PY -m pytest -q -x --timeout 1400 backends/direct/ligerito/live_session_gpu_test.py backends/direct/ligerito/live_session_test.py > $O/live_session_tests.log 2>&1; echo "live_session tests exit $?" > $O/summary.txt
