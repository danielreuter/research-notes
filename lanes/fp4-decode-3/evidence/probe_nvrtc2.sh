#!/usr/bin/env bash
# lane fp4-decode-3: the fused witness kernel of fp4-nvf4+poseidon2 (/tmp/wit.cu, dumped by probe_nvrtc.sh): front end (cicc, nvcc -ptx)
# for compute_120 vs compute_89 in parallel, then ptxas sm_120 on the compute_89 PTX (the "PTX for an older arch, JIT to sm_120" route).
set -uo pipefail
export PATH=/usr/local/cuda/bin:$PATH
T() { local s=$(date +%s.%N); "$@" > /tmp/probe2.$$.$RANDOM.out 2>&1; local rc=$?; printf "%7.1fs rc=%d  %s\n" "$(echo "$(date +%s.%N) - $s" | bc)" $rc "$*"; }
( T timeout 900 nvcc -std=c++17 -ptx -arch=compute_120 /tmp/wit.cu -o /tmp/wit120.ptx ) &
( T timeout 900 nvcc -std=c++17 -ptx -arch=compute_89 /tmp/wit.cu -o /tmp/wit89.ptx
  ls -la /tmp/wit89.ptx
  T timeout 900 ptxas -arch=sm_89 /tmp/wit89.ptx -o /tmp/w89.cubin
  T timeout 900 ptxas -arch=sm_120 /tmp/wit89.ptx -o /tmp/w89on120.cubin ) &
wait
echo PROBE2_DONE
