#!/usr/bin/env bash
# red-team-flock-2: PR #54 @ 34d02ae3 (IR1/IR2 fix, the RMSNorm templates, flock-ir-unit/v2), CPU only.
#  0. netlists (rope, silu, fused, triton) and the MUFU tables generated here from the source (pins checked)
#  1. ir_tail primitives (rtf2-tail harness) vs the IR primitives, bit for bit (tail_diff.py)
#  2. rmsnorm-triton units vs the IR evaluator on adversarial rows (rms_check.py; fused ran on the VM), staged files
#  3. load check (the Rust tail on every instance) on the adversarial fused / triton files: must pass
#  4. full selftest (13 cut cases) on small fused / triton files; rope / silu selftests under v2 (11 cases)
#  5. cut-accounting tampers (must be refused at load) and the consistent eps forgery (IR4)
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O; SRC=$(pwd)
sha256sum $I/* | tee $O/inputs.sha256
cp $I/rtf2_tail.rs backends/flock/live/src/bin/rtf2-tail.rs
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build-base.txt 2>&1 || { tail -60 $O/build.txt; exit 1; }
source $HOME/.cargo/env
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export RAYON_NUM_THREADS=$TH
W=/workspace/flock-gpu-link/flock
(cd $W && cargo build --release -p flock-live --bin flock-ir-block --bin rtf2-tail -j $TH) > $O/build-ir.txt 2>&1 || { tail -40 $O/build-ir.txt; exit 1; }
P=$W/target/release/flock-ir-block; H=$W/target/release/rtf2-tail; sha256sum $P $H | tee $O/binary.sha256
# the verity packages need Python >= 3.12 (PEP 695); the pod image has 3.11
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh > $O/uv-install.txt 2>&1; }
export PATH=$HOME/.local/bin:$HOME/.cargo/bin:$PATH
uv python install 3.12 > $O/uv-python.txt 2>&1 || { tail -5 $O/uv-python.txt; exit 1; }
PY="uv run --python 3.12 --no-project --with numpy python3"
$PY -c "import sys, numpy; print('PY', sys.version.split()[0], 'numpy', numpy.__version__)" || exit 1
export PYTHONPATH=$SRC/backends/flock/python:$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/integrations/vllm:$SRC/backends/direct
N=$O/nets; T=$O/tables; D=$O/files; mkdir -p $N $T $D
$PY - <<'EOF' 2>&1 | tee $O/gen.txt
import hashlib, importlib, os
from verity_numerical.bench import lowerings, templates as TM
import verity_flock.ir_lower as IL
O = os.environ["RESEARCH_RUN_DIR"] + "/out"
REG = lowerings.registry("C-Flock")
for t, p in (("rope-head", {"D": 64}), ("silu-mul", {"I": 8192}), ("rmsnorm-fused-cuda", {"N": 2048, "EPS": 1e-5}), ("rmsnorm-triton", {"N": 2048, "EPS": 1e-5})):
    low = REG.module(t).lowering(TM.subcircuit(t, **p))
    tm = importlib.import_module("verity_flock.templates." + t.replace("-", "_"))
    pin = tm.PIN if hasattr(tm, "PIN") else tm.PINS[2048]
    s = hashlib.sha256(low.text.encode()).hexdigest()
    open(f"{O}/nets/net-{t}.txt", "w").write(low.text); open(f"{O}/nets/pin-{t}", "w").write(s)
    print("NET", t, s, "pin ok", s == pin)
print("TABLES", IL.write_tables(O + "/tables"))
EOF
pin() { cat $N/pin-$1; }
$PY $I/tail_diff.py $H $T 1024 > $O/tail-diff.txt 2>&1; cat $O/tail-diff.txt
$PY $I/rms_check.py rmsnorm-triton $N/net-rmsnorm-triton.txt 130 $D 13 > $O/rms-triton-130.txt 2>&1; cat $O/rms-triton-130.txt
$PY $I/rms_check.py rmsnorm-triton $N/net-rmsnorm-triton.txt 4 $D 17 --no-units > $O/rms-triton-4.txt 2>&1; tail -1 $O/rms-triton-4.txt
$PY $I/rms_check.py rmsnorm-fused-cuda $N/net-rmsnorm-fused-cuda.txt 260 $D 19 --no-units > $O/rms-fused-260.txt 2>&1; cat $O/rms-fused-260.txt
cp $I/inst-rmsnorm-fused-cuda-adv-240.bin $I/inst-rmsnorm-fused-cuda-neareps-4.bin $D/
ld() {  # tag template file
  $P loadcheck --instances $2 --netlist $N/net-$1.txt --pin $(pin $1) --tables $T > $O/$3.txt 2>&1; local rc=$?
  echo "== $3 rc=$rc $(grep -h 'REFUSED\|^statement' $O/$3.txt | head -1 | cut -c1-230)"
}
[ -s $N/net-rmsnorm-fused-cuda.txt ] || { echo "no netlists generated"; exit 1; }
ld rmsnorm-fused-cuda $D/inst-rmsnorm-fused-cuda-adv-240.bin L-fused-adv-240
ld rmsnorm-fused-cuda $D/inst-rmsnorm-fused-cuda-adv-260.bin L-fused-adv-260
ld rmsnorm-triton $D/inst-rmsnorm-triton-adv-130.bin L-triton-adv-130
st() {  # tag template file [args]
  local t=$1 f=$2 tag=$3; shift 3
  $P selftest --instances $f --netlist $N/net-$t.txt --pin $(pin $t) --tables $T "$@" > $O/$tag.txt 2>&1; local rc=$?
  echo "== $tag rc=$rc"; grep -h 'SELFTEST\|"pass":false\|REFUSED\|^NEG' $O/$tag.txt | cut -c1-300
}
st rmsnorm-fused-cuda $D/inst-rmsnorm-fused-cuda-neareps-4.bin S-fused-4
st rmsnorm-triton $D/inst-rmsnorm-triton-adv-4.bin S-triton-4
$PY $I/gen_ir_inst.py rope $N/net-rope-head.txt 256 $D/inst-rope-256.bin 1 > /dev/null && st rope-head $D/inst-rope-256.bin S-rope-256
$PY $I/gen_ir_inst.py silu $N/net-silu-mul.txt 8192 $D/inst-silu-8192.bin 3 > /dev/null && st silu-mul $D/inst-silu-8192.bin S-silu-8192
for f in $I/t-*.bin; do ld rmsnorm-fused-cuda $f L-$(basename $f .bin); done
st rmsnorm-fused-cuda $I/t-eps_forged_consistent.bin S-eps-forged --only honest
true
