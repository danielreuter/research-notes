#!/usr/bin/env bash
# red-team-flock-2: the served workloads' elementwise pins at a8ce768a (verity/flock-ir-frame/v3), CPU only (92-ew.sh = 90-ir6.sh
# with the new parameters: rope D=128, silu I=9728, rmsnorm-triton N=4096 / N=128 eps 1e-6, rmsnorm-fused-cuda N=4096).
#  1. build flock-ir-frame; stage synthetic sets (rope 16, silu 2, fused 3, triton 3 instances) by ir_frame.stage; each pin, and
#     the pin of its text without the LEAVES line (the rows' granted pin)
#  2. the producer's selftest on each (its four IR6 cases included)
#  3. my 07:55Z tampers (frame_tamper.py) at load, and the two c53d9148 accepted (wiring_swap, key_changed) as sessions
#  4. my IR6 tampers (ir6_tamper.py) at load under the verifier's pin; the tampered netlists also unpinned
set -uxo pipefail
# env: SRCSHA (the shipped source), SKIP_SELFTEST=1 (tampers only)
[ -d backends/flock ] || cd /workspace/research/src/${RESEARCH_SOURCE_SHA:-${SRCSHA:-a8ce768a}} || exit 1
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O; SRC=$(pwd)
sha256sum $I/* | tee $O/inputs.sha256
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build-base.txt 2>&1 || { tail -60 $O/build-base.txt; exit 1; }
source $HOME/.cargo/env
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export RAYON_NUM_THREADS=$TH
W=/workspace/flock-gpu-link/flock
(cd $W && cargo build --release -p flock-live --bin flock-ir-frame -j $TH) > $O/build-ir.txt 2>&1 || { tail -40 $O/build-ir.txt; exit 1; }
PF=$W/target/release/flock-ir-frame; sha256sum $PF | tee $O/binary.sha256
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh > $O/uv-install.txt 2>&1; }
export PATH=$HOME/.local/bin:$HOME/.cargo/bin:$PATH
uv python install 3.12 > $O/uv-python.txt 2>&1 || { tail -5 $O/uv-python.txt; exit 1; }
PY="uv run --python 3.12 --no-project --with numpy --with blake3 python3"
export PYTHONPATH=$SRC/backends/flock/python:$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/integrations/vllm:$SRC/backends/direct
D=$O/files; T=$O/tables; mkdir -p $D $T
$PY - <<'EOF' 2>&1 | tee $O/stage.txt
import hashlib, importlib, os
from verity_numerical.bench import templates as TM
from verity_numerical.bench.generate import generate
from verity_numerical.bench.input_sets import InputSet
import verity_flock.ir_lower as IL
from verity_flock import ir_frame
print('SOURCE', os.getcwd())
O = os.environ["RESEARCH_RUN_DIR"] + "/out"; D = O + "/files"
print("TABLES", IL.write_tables(O + "/tables"))
P = {"rope-head": ({"D": 128}, 16), "silu-mul": ({"I": 9728}, 2), "rmsnorm-fused-cuda": ({"N": 4096, "EPS": 1e-5}, 2), "rmsnorm-triton": ({"N": 4096, "EPS": 1e-5}, 2), "rmsnorm-triton-n128": ({"N": 128, "EPS": 1e-6}, 8)}
for t, (params, n) in P.items():
    tpl = t.replace("-n128", "")
    sub = TM.subcircuit(tpl, **params)
    s = InputSet.open(generate(sub, n, 20260926, f"{D}/set-{t}")["path"])
    mod = importlib.import_module("verity_flock.templates." + tpl.replace("-", "_"))
    low = mod.frame_lowering(sub)
    p = ir_frame.stage(low, s, 0, n, f"{D}/fr-{t}")
    pin = hashlib.sha256(low.text.encode()).hexdigest()
    open(f"{D}/fr-{t}/pin", "w").write(pin)
    rows = "".join(l + "\n" for l in low.text.splitlines() if not l.startswith("LEAVES "))
    print("FRAME", t, p, "pin", pin[:8], "without LEAVES", hashlib.sha256(rows.encode()).hexdigest()[:8])
EOF
fr() {  # template file tag [args]: CMD (selftest | loadcheck), NET (default the staged netlist), PINNED (1: the verifier's pin)
  local t=$1 f=$2 tag=$3; shift 3; local d=$D/fr-$t
  local pin=(); [ "${PINNED:-1}" = 1 ] && pin=(--pin $(cat $d/pin))
  $PF ${CMD:-selftest} --instances $f --netlist ${NET:-$d/net.txt} "${pin[@]}" --tables $T "$@" > $O/$tag.txt 2>&1; local rc=$?
  echo "== $tag rc=$rc $(grep -h 'SELFTEST\|REFUSED\|^statement\|panicked' $O/$tag.txt | head -1 | cut -c1-260)"; grep -h '"pass":false' $O/$tag.txt | cut -c1-250
}
for t in rope-head silu-mul rmsnorm-fused-cuda rmsnorm-triton rmsnorm-triton-n128; do
  F=$(ls $D/fr-$t/frame-*.bin | head -1)
  [ "${SKIP_SELFTEST:-0}" = 1 ] || fr $t $F S-$t
  grep -h '"case":"\(wiring_swapped\|output_mapping_swapped\|units_swapped_between_slots\|row_key_changed\)"' $O/S-$t.txt | cut -c1-300
  FT=$D/ft-$t; mkdir -p $FT
  $PY $I/frame_tamper.py $F $FT > $O/frame-tamper-$t.txt 2>&1
  $PY $I/ir6_tamper.py $F $D/fr-$t/net.txt $FT > $O/ir6-tamper-$t.txt 2>&1; cat $O/ir6-tamper-$t.txt
  for f in $FT/f-*.bin; do
    c=$(basename $f .bin); c=${c#f-}; n=$FT/n-$c.txt
    if [ -f $n ]; then
      NET=$n CMD=loadcheck fr $t $f L-$t-$c-pinned
      NET=$n CMD=loadcheck PINNED=0 fr $t $f L-$t-$c-unpinned
    else
      CMD=loadcheck fr $t $f L-$t-$c
    fi
  done
  [ "${SKIP_SELFTEST:-0}" = 1 ] || for c in wiring_swap key_changed; do fr $t $FT/f-$c.bin H-$t-$c --only honest; grep -h '^NEG' $O/H-$t-$c.txt | grep -o '"accepted":[a-z]*' | head -1; done
done
true
