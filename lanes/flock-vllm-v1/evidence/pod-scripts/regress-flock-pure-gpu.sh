set -ux
O=$RESEARCH_RUN_DIR/out; mkdir -p $O; REPO=$(pwd)
export PATH=/workspace/flock-vllm-v1/py/bin:$PATH PYTHONPATH=$REPO/packages/verity/src:$REPO/backends/numerical/python:$REPO/backends/flock/python
C13=/usr/local/cuda-13.3; export LD_LIBRARY_PATH=$C13/compat:$C13/lib64:${LD_LIBRARY_PATH:-} RAYON_NUM_THREADS=32
python3 -c "
from verity_flock import instances, lowering
open('$O/net.txt','w').write(lowering.netlist('fp8-hopper'))
instances.write('$O/inst-8.bin','fp8-hopper',8,procs=8)"
P=/workspace/flock-gpu-link/flock/target/release/flock-pure-gpu; sha256sum $P
$P selftest --gpu --instances $O/inst-8.bin --netlist $O/net.txt > $O/pure-gpu-selftest-8.txt 2>&1; grep -h 'SELFTEST\|"pass":false' $O/pure-gpu-selftest-8.txt | cut -c1-300
