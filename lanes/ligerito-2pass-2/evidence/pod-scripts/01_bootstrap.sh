# prover pod vy-ligerito-2pass (4090), tree /workspace/src @ e0c7acd2
mkdir -p /workspace/ligerito-2pass-2
cd /workspace && nohup bash -c 'RELS=fp8-ada NS=4096 bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh' > /workspace/ligerito-2pass-2/bootstrap.log 2>&1 &
