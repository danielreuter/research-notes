#!/usr/bin/env bash
# lane fp4-decode-3: why the fused witness kernel of fp4-nvf4+poseidon2 takes minutes to build on the 5090 (sm_120) but seconds
# on the 4090 (sm_89): dump the generated source, then time front end (nvcc -ptx) and back end (ptxas) per arch / -O level.
set -uo pipefail
cd /workspace/research/src/d86e0145d1e6ae055086004c852783d8f318f8f7
export PATH=/workspace/venv312/bin:/usr/local/cuda/bin:$PATH PYTHONPATH=$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD
python - <<'PY'
from backends.direct.ligero.fp4.hashed import FP4_HASHED
from backends.direct.ligero import witness_device as wd, hashchain
sys = hashchain.compose(FP4_HASHED).sys
prog = wd._program(sys)
tab = [] if wd._n_terms(prog) > wd.TAB_THRESHOLD else None
src = wd.generate(sys, tab, prog)
open("/tmp/wit.cu", "w").write(src)
print("m", sys.m, "terms", wd._n_terms(prog), "tab", None if tab is None else len(tab), "src bytes", len(src), "lines", src.count("\n"),
      "CHUNK_OPS", wd.CHUNK_OPS)
PY
nvcc --version | tail -2
T() { local s=$(date +%s.%N); "$@" > /tmp/probe.out 2>&1; local rc=$?; printf "%6.1fs rc=%d  %s\n" "$(echo "$(date +%s.%N) - $s" | bc)" $rc "$*"; }
T nvcc -std=c++17 -ptx -arch=compute_120 /tmp/wit.cu -o /tmp/wit120.ptx
T nvcc -std=c++17 -ptx -arch=compute_89 /tmp/wit.cu -o /tmp/wit89.ptx
ls -la /tmp/wit120.ptx /tmp/wit89.ptx
( T ptxas -arch=sm_89 /tmp/wit89.ptx -o /tmp/w89.cubin ) &
( T timeout 300 ptxas -arch=sm_120 -O1 /tmp/wit120.ptx -o /tmp/w120o1.cubin ) &
( T timeout 300 ptxas -arch=sm_120 -O0 /tmp/wit120.ptx -o /tmp/w120o0.cubin ) &
( T timeout 300 ptxas -arch=sm_120 /tmp/wit120.ptx -o /tmp/w120.cubin ) &
wait
