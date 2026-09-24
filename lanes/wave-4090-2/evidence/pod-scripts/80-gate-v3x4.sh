#!/usr/bin/env bash
# wave-4090-2: the headline relation's gate, which integration could not finish at 4096 VUs (49 honest sub-batches vs the CPU
# Python hint reference, >50 min): fp8-ada-v3x4 fused, --batch 4096, at 1024 VUs (brief §4), zk interactive, local coins.
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
O=/workspace/wave-4090/gates; mkdir -p $O
t0=$(date +%s)
$PY -m backends.direct.ligero.run --relation fp8-ada-v3x4 gate-vu --vus 1024 --batch 4096 --zk --mode interactive \
    --out $O/fp8-ada-v3x4-bare-1024.json > $O/fp8-ada-v3x4-bare-1024.log 2>&1
echo "fp8-ada-v3x4-bare-1024 rc=$? $(( $(date +%s) - t0 ))s :: $(grep -E 'gate: .* failures' $O/fp8-ada-v3x4-bare-1024.log | tail -1)" | tee -a $O/summary.txt
