#!/usr/bin/env bash
# red-team-flock-2: fp4-nvf4 layouts at flock-gpu-link 0bb25e8a (the handed-off commit; 7b3ba797 + a GPU-only gpu.rs fix), CPU
# only, at VU counts that are not powers of two, so dummy blocks exist (12 VUs: 4 dummies; 40 VUs: 24). Producer selftest on
# my gen_fp4.py files, plus a forged dummy block per layout (rtf2_patch.py).
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
sha256sum $I/* | tee $O/inputs.sha256
F=backends/flock/live/src/bin/flock-pure-gpu.rs
cp $F $O/flock-pure-gpu.rs.orig
python3 $I/rtf2_patch.py $F | tee $O/patch.txt || exit 1
diff -u $O/flock-pure-gpu.rs.orig $F > $O/rtf2.diff
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build-patched.txt 2>&1 || { tail -60 $O/build.txt; exit 1; }
source $HOME/.cargo/env
P=/workspace/flock-gpu-link/flock/target/release/flock-pure-gpu
N=$I/net-fp4-nvf4.txt; PIN=fb52a87c01a8a41f0e3460a10c62dcac4c346eb0c4540a86e0921845738666b3
sha256sum $P | tee $O/binary.sha256
run() { local tag=$1; shift; $P selftest --netlist $N --pin $PIN "$@" > $O/$tag.txt 2>&1; echo "== $tag"; grep -h 'SELFTEST\|"pass":false\|^NEG' $O/$tag.txt | cut -c1-420; }
for s in b3 sha; do for n in 12 40; do run selftest-$s-$n --instances $I/inst-fp4-$s-$n.bin; done; done
run neg-b3-fp4_dummy_block_forged --instances $I/inst-fp4-b3-12.bin --only fp4_dummy_block_forged
run neg-sha-sha_fp4_dummy_block_forged --instances $I/inst-fp4-sha-12.bin --only sha_fp4_dummy_block_forged
true
