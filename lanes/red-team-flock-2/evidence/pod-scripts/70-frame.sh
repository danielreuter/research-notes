#!/usr/bin/env bash
# red-team-flock-2: PR #54 @ c53d9148 (verity/flock-ir-frame/v2; IR4/IR5 at b4e05b48 are ancestors), CPU only.
#  1. IR5: ir_tail primitives vs the IR (tail_diff.py): every primitive, two-NaN cases included, must be 0 mismatches
#  2. IR4: flock-ir-block on a fused block file: a header carrying its own cut, cut_words + 1, a netlist whose CUT line differs
#  3. frame: synthetic sets staged by ir_frame.stage (rope 16, silu 2, fused 3, triton 3 instances); the producer's selftest;
#     my RT2 attacks (rtf2_frame_patch.py); verifier-file tampers (frame_tamper.py) at load
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O; SRC=$(pwd)
sha256sum $I/* | tee $O/inputs.sha256
cp $I/rtf2_tail.rs backends/flock/live/src/bin/rtf2-tail.rs
F=backends/flock/live/src/bin/flock-ir-frame.rs; cp $F $O/flock-ir-frame.rs.orig
python3 $I/rtf2_frame_patch.py $F | tee $O/patch.txt || exit 1
diff -u $O/flock-ir-frame.rs.orig $F > $O/rtf2-frame.diff
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build-base.txt 2>&1 || { tail -60 $O/build.txt; exit 1; }
source $HOME/.cargo/env
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export RAYON_NUM_THREADS=$TH
W=/workspace/flock-gpu-link/flock
(cd $W && cargo build --release -p flock-live --bin flock-ir-frame --bin flock-ir-block --bin rtf2-tail -j $TH) > $O/build-ir.txt 2>&1 || { tail -40 $O/build-ir.txt; exit 1; }
PF=$W/target/release/flock-ir-frame; PB=$W/target/release/flock-ir-block; H=$W/target/release/rtf2-tail; sha256sum $PF $PB $H | tee $O/binary.sha256
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh > $O/uv-install.txt 2>&1; }
export PATH=$HOME/.local/bin:$HOME/.cargo/bin:$PATH
uv python install 3.12 > $O/uv-python.txt 2>&1 || { tail -5 $O/uv-python.txt; exit 1; }
PY="uv run --python 3.12 --no-project --with numpy --with blake3 python3"
export PYTHONPATH=$SRC/backends/flock/python:$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/integrations/vllm:$SRC/backends/direct
D=$O/files; T=$O/tables; mkdir -p $D $T
$PY - <<'EOF' 2>&1 | tee $O/stage.txt
import hashlib, importlib, json, os
from verity_numerical.bench import templates as TM
from verity_numerical.bench.generate import generate
from verity_numerical.bench.input_sets import InputSet
import verity_flock.ir_lower as IL
from verity_flock import ir_frame
O = os.environ["RESEARCH_RUN_DIR"] + "/out"; D = O + "/files"
print("TABLES", IL.write_tables(O + "/tables"))
P = {"rope-head": ({"D": 64}, 16), "silu-mul": ({"I": 8192}, 2), "rmsnorm-fused-cuda": ({"N": 2048, "EPS": 1e-5}, 3), "rmsnorm-triton": ({"N": 2048, "EPS": 1e-5}, 3)}
for t, (params, n) in P.items():
    sub = TM.subcircuit(t, **params)
    s = InputSet.open(generate(sub, n, 20260926, f"{D}/set-{t}")["path"])
    mod = importlib.import_module("verity_flock.templates." + t.replace("-", "_"))
    low = mod.frame_lowering(sub)
    p = ir_frame.stage(low, s, 0, n, f"{D}/fr-{t}")
    open(f"{D}/fr-{t}/pin", "w").write(hashlib.sha256(low.text.encode()).hexdigest())
    print("FRAME", t, p, hashlib.sha256(low.text.encode()).hexdigest()[:16])
    if t == "rmsnorm-fused-cuda":
        lb = mod.lowering(sub)
        q = IL.stage(lb, s, 0, n, f"{D}/bl-{t}")
        open(f"{D}/bl-{t}/pin", "w").write(hashlib.sha256(lb.text.encode()).hexdigest())
        b = open(q, "rb").read(); nl = b.index(b"\n"); h = json.loads(b[:nl])
        for name, edit in (("header_cut", lambda x: x.__setitem__("cut", {"words": x["cut_words"]})),
                           ("cut_words_plus1", lambda x: x.__setitem__("cut_words", x["cut_words"] + 1))):
            hh = json.loads(b[:nl]); edit(hh)
            open(f"{D}/bl-{t}/b-{name}.bin", "wb").write(json.dumps(hh, sort_keys=True).encode() + b"\n" + b[nl + 1:])
        text = open(f"{D}/bl-{t}/net.txt").read()
        open(f"{D}/bl-{t}/net-cut-eps.txt", "w").write(text.replace("925353388", "981668463"))   # the CUT line's eps: 1e-5 -> 1e-3
        print("BLOCK", t, q)
EOF
$PY $I/tail_diff.py $H $T 512 > $O/tail-diff.txt 2>&1; cat $O/tail-diff.txt
bl() {  # tag instances netlist pin
  $PB loadcheck --instances $2 --netlist $3 ${4:+--pin $4} --tables $T > $O/$1.txt 2>&1; local rc=$?
  echo "== $1 rc=$rc $(grep -h 'REFUSED\|^statement\|panicked' $O/$1.txt | head -1 | cut -c1-230)"
}
B=$D/bl-rmsnorm-fused-cuda; BP=$(cat $B/pin)
bl IR4-honest $B/inst-3.bin $B/net.txt $BP
bl IR4-header-cut $B/b-header_cut.bin $B/net.txt $BP
bl IR4-cut-words-plus1 $B/b-cut_words_plus1.bin $B/net.txt $BP
bl IR4-netlist-eps-pinned $B/inst-3.bin $B/net-cut-eps.txt $BP
bl IR4-netlist-eps-unpinned $B/inst-3.bin $B/net-cut-eps.txt ""
bl IR4-old-format-eps-forged $I/t-eps_forged_consistent.bin $B/net.txt $BP
fr() {  # tag template file [args]
  local t=$1 f=$2 tag=$3; shift 3; local d=$D/fr-$t
  $PF ${CMD:-selftest} --instances $f --netlist $d/net.txt --pin $(cat $d/pin) --tables $T "$@" > $O/$tag.txt 2>&1; local rc=$?
  echo "== $tag rc=$rc $(grep -h 'SELFTEST\|REFUSED\|panicked' $O/$tag.txt | head -1 | cut -c1-230)"; grep -h '"pass":false' $O/$tag.txt | cut -c1-250
}
for t in rope-head silu-mul rmsnorm-fused-cuda rmsnorm-triton; do fr $t $(ls $D/fr-$t/frame-*.bin | head -1) S-$t; done
for t in rmsnorm-fused-cuda rmsnorm-triton; do
  for a in counter_forged blen_forged empty_run_message empty_run_published empty_unit_input public_other_run; do
    RT2=$a fr $t $(ls $D/fr-$t/frame-*.bin | head -1) A-$t-$a --only honest; grep -h '^NEG' $O/A-$t-$a.txt | grep -o '"accepted":[a-z]*' | head -1
  done
done
FT=$D/ft; mkdir -p $FT; $PY $I/frame_tamper.py $(ls $D/fr-rmsnorm-fused-cuda/frame-*.bin | head -1) $FT > $O/frame-tamper.txt 2>&1; cat $O/frame-tamper.txt
for f in $FT/f-*.bin; do CMD=loadcheck fr rmsnorm-fused-cuda $f L-$(basename $f .bin); done
for f in f-wiring_swap f-key_changed; do fr rmsnorm-fused-cuda $FT/$f.bin H-$f --only honest; grep -h '^NEG' $O/H-$f.txt | grep -o '"accepted":[a-z]*' | head -1; done
true
