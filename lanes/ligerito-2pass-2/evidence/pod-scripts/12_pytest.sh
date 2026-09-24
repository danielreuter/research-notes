# full backends/direct/ligerito pytest suite at 0f6cc311 on the 4090 (bounded 15 min)
source /workspace/env.sh; cd /workspace/src; O=/workspace/ligerito-2pass-2/tests
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
timeout 900 $PY -m pytest -q -rfEs --timeout 800 -p no:cacheprovider backends/direct/ligerito > $O/pytest_ligerito.log 2>&1; echo "pytest ligerito exit $?" >> $O/summary.txt
