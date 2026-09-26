#!/usr/bin/env bash
# red-team-flock-2: verity/flock-ir-block/v1 (PR #54 @ 366befc4), CPU only, on my own instance files (gen_ir_inst.py).
#  1. the producer's selftest (+ --precheck) on rope 256 / 5000 units and silu 300 / 3000 units (padding units in each)
#  2. RT2 attacks (rtf2_ir_patch.py, `--only honest`): padding unit with nonzero inputs, swapped units, unit 3's constant
#     row, an unused input bit, a claimed unused output bit
#  3. header tampers: another unit's netlist sha, in_words 2, cut_words 1
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
sha256sum $I/* | tee $O/inputs.sha256
F=backends/flock/live/src/bin/flock-ir-block.rs
cp $F $O/flock-ir-block.rs.orig
python3 $I/rtf2_ir_patch.py $F | tee $O/patch.txt || exit 1
diff -u $O/flock-ir-block.rs.orig $F > $O/rtf2-ir.diff
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build-base.txt 2>&1 || { tail -60 $O/build.txt; exit 1; }
source $HOME/.cargo/env
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export RAYON_NUM_THREADS=$TH
W=/workspace/flock-gpu-link/flock
(cd $W && cargo build --release -p flock-live --bin flock-ir-block -j $TH) > $O/build-ir.txt 2>&1 || { tail -40 $O/build-ir.txt; exit 1; }
P=$W/target/release/flock-ir-block; sha256sum $P | tee $O/binary-ir.sha256
ROPE=25d8e464dd56a99d65027d1f010ea0c29a5066679108854b73a5120bbcdbffb9; SILU=5bb4a943ff542becf69b56b80b9596107b90b23926df191b6fe419a96bade0fd
run() {  # tag file RT2 [args...]
  local tag=$1 f=$2 rt=$3; shift 3; local net=$I/net-rope-head.txt pin=$ROPE
  case $f in *silu*) net=$I/net-silu-mul.txt; pin=$SILU;; esac
  RT2=$rt $P selftest --instances $I/$f --netlist $net --pin $pin "$@" > $O/$tag.txt 2>&1; local rc=$?
  echo "== $tag rc=$rc"; grep -h 'PRECHECK\|SELFTEST\|"pass":false\|^RT2\|panicked' $O/$tag.txt | cut -c1-300
}
for f in inst-rope-256 inst-rope-5000 inst-silu-300 inst-silu-3000; do run A-$f $f.bin "" --precheck; done
for f in inst-rope-256 inst-silu-300; do
  for a in padding_nonzero_input swap_units_0_1 const_row_flip_u3 unused_input_bit_u2 out_unused_bit_claim; do run B-$f-$a $f.bin $a --only honest; done
done
for f in inst-rope-256-wrongsha inst-rope-256-inwords2 inst-rope-256-cut1; do run C-$f $f.bin "" --only honest; done
true
