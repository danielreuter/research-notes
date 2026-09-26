#!/usr/bin/env bash
# flock-ir-sampling: verity/flock-ir-sampling/v1 (the flock-ir-sampling binary) on the GPU. Builds flock-gpu-link's checkout
# (20-gpu-link.sh MODE=build) and flock-ir-sampling, stages a synthetic GumbelTopPTokenSelect_v1{V=SELF_V} set on the pod
# (verity_flock.ir_sampling.stage: the verifier's own staging), runs the CPU and GPU selftests on it, then loopback sessions (WARM
# warm-ups + RUNS timed, --gpu) on the first LOOP rows of the input set sent as inputs/*.tar (research run --send), if any.
# env: SELF_V=1280 SELF_N=2  LOOP="1 4"  WARM=1 RUNS=2  GPU=1  SM (default: the GPU's compute capability from nvidia-smi)
for kv in "$@"; do case $kv in *=*) export "$kv" ;; esac; done
set -uxo pipefail
SRC=$(pwd); I=${RESEARCH_RUN_DIR:-/tmp/fis}/inputs; O=${RESEARCH_RUN_DIR:-/tmp/fis}/out; W=/workspace/flock-ir; mkdir -p $O $W
[ -x /usr/bin/time ] || { apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq time >/dev/null; }
SM=${SM:-$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -1 | tr -d .)}; SM=${SM:-90}
MODE=build GPU=${GPU:-1} SM=$SM bash backends/flock/pod/20-gpu-link.sh > $O/build.log 2>&1 || { tail -30 $O/build.log; exit 1; }
source $HOME/.cargo/env; C13=/usr/local/cuda-13.3; export PATH=$C13/bin:$PATH NVCC=$C13/bin/nvcc LD_LIBRARY_PATH=$C13/compat:$C13/lib64:${LD_LIBRARY_PATH:-}
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export RAYON_NUM_THREADS=$TH
F=/workspace/flock-gpu-link/flock
FEAT=; G=; [ "${GPU:-1}" = 1 ] && { FEAT="--features gpu"; G=--gpu; }
(cd $F && cargo build --release -p flock-live $FEAT --bin flock-ir-sampling -j $TH) > $O/build-ir.txt 2>&1 || { tail -40 $O/build-ir.txt; exit 1; }
B=$F/target/release/flock-ir-sampling; sha256sum $B | tee $O/binary.sha256
[ -x $HOME/.local/bin/uv ] || curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
[ -x $W/py/bin/python ] || { $HOME/.local/bin/uv venv -q --python 3.12 $W/py && $HOME/.local/bin/uv pip install -q --python $W/py/bin/python numpy blake3; }
export PATH=$W/py/bin:$PATH PYTHONPATH=$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/backends/flock/python:$SRC/integrations/vllm
lscpu | grep -E 'Model name|^CPU\(s\)' | tee $O/host.txt; echo threads $TH | tee -a $O/host.txt; nvidia-smi -L 2>/dev/null | tee -a $O/host.txt
python3 - <<EOF > $O/stage-self.txt 2>&1 || { tail -20 $O/stage-self.txt; exit 1; }
from verity_flock import ir_sampling as S, ir_lower as IL
from verity_numerical.bench import templates as TM
from verity_numerical.bench.generate import generate
from verity_numerical.bench.input_sets import InputSet
V = int("${SELF_V:-1280}")
s = InputSet.open(generate(TM.subcircuit(S.TEMPLATE, V=V), int("${SELF_N:-2}"), 20260926, "$W/self")["path"])
p = S.stage(S.lane(V), s, 0, s.n, "$W/self/st")
IL.write_tables("$W/tables")
print(p, S.public_sha256(p), S.check_native(p))
EOF
cat $O/stage-self.txt
$B selftest --tables $W/tables --instances $W/self/st/frame-${SELF_N:-2}.bin --netlist $W/self/st/net.txt > $O/selftest-cpu.txt 2>&1
grep -h 'SELFTEST\|"pass":false\|REFUSED' $O/selftest-cpu.txt | cut -c1-400
[ -n "$G" ] && { $B selftest --gpu --tables $W/tables --instances $W/self/st/frame-${SELF_N:-2}.bin --netlist $W/self/st/net.txt > $O/selftest-gpu.txt 2>&1;
                 grep -h 'SELFTEST\|"pass":false\|REFUSED' $O/selftest-gpu.txt | cut -c1-400; }
TAR=$(ls $I/*.tar 2>/dev/null | head -1)
[ -z "$TAR" ] && exit 0
rm -rf $W/set && mkdir -p $W/set && tar -xf $TAR -C $W/set || exit 1
SET=$(dirname $(find $W/set -name manifest.json | head -1))
for n in ${LOOP-1 4}; do
  python3 -c "
from verity_flock import ir_sampling as S
from verity_numerical.bench.input_sets import InputSet
s = InputSet.open('$SET'); p = S.stage(S.lane(int(s.subcircuit.params['V'])), s, 0, $n, '$W/loop-$n')
print(p, S.serve_args(p)[1])" > $O/stage-loop-$n.txt 2>&1 || { tail -5 $O/stage-loop-$n.txt; continue; }
  CHK=$(tail -1 $O/stage-loop-$n.txt | cut -d' ' -f2); NET=$W/loop-$n/net.txt; PIN=$(sha256sum $NET | cut -d' ' -f1)
  $B serve --listen 127.0.0.1:7402 --out $O/sessions-loop-$n --tables $W/tables --instances $W/loop-$n/frame-$n.bin --netlist $NET --pin $PIN \
     --native-checked $CHK --operator loopback > $O/serve-loop-$n.log 2>&1 &
  SP=$!
  for i in $(seq 900); do grep -q 'SERVING\|REFUSED' $O/serve-loop-$n.log && break; sleep 1; done
  /usr/bin/time -v -o $O/prove-loop-$n.time $B prove --verifier 127.0.0.1:7402 --tables $W/tables --instances $W/loop-$n/frame-$n.bin --netlist $NET $G \
     --warm ${WARM:-1} --runs ${RUNS:-2} > $O/prove-loop-$n.txt 2>&1
  grep -h "^LIVE\|panicked\|REFUSED" $O/prove-loop-$n.txt | cut -c1-1200; grep -h "Maximum resident\|Elapsed" $O/prove-loop-$n.time
  kill $SP; wait $SP 2>/dev/null
done
true
