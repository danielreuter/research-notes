#!/usr/bin/env bash
# red-team-flock-2: the NVFP4 block layouts (Fp4 / ShaFp4) of flock-pure-block at flock-gpu-link 7b3ba797, CPU only.
# Source: 7b3ba797 (research run --source <clean checkout> --cwd source). Inputs: my gen_fp4.py instance files, the regenerated
# fp4-nvf4 netlist (pin fb52a87c), rtf2_patch.py (prover-side attack knobs; PureVerifier and pure_block.rs untouched).
#  1. the producer's selftest on my instance files (Fp4 and ShaFp4, 8 and 64 VUs);
#  2. my NVFP4 negatives (each must be refused);
#  3. file-level gaps: honest proofs on tampered statement files (y != out, schema relabel);
#  4. G2: the fp4 netlist under the Fp8 layout, prover-chosen scales over the same committed rows.
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
sha256sum $I/* | tee $O/inputs.sha256
F=backends/flock/live/src/bin/flock-pure-gpu.rs
cp $F $O/flock-pure-gpu.rs.orig
python3 $I/rtf2_patch.py $F | tee $O/patch.txt || exit 1
diff -u $O/flock-pure-gpu.rs.orig $F > $O/rtf2.diff
PATCHED=1
if ! MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build-patched.txt 2>&1; then
  tail -60 $O/build.txt; PATCHED=0; cp $O/flock-pure-gpu.rs.orig $F
  MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build-unpatched.txt 2>&1 || { tail -60 $O/build.txt; exit 1; }
fi
echo "PATCHED=$PATCHED"
source $HOME/.cargo/env
P=/workspace/flock-gpu-link/flock/target/release/flock-pure-gpu
N=$I/net-fp4-nvf4.txt; PIN=fb52a87c01a8a41f0e3460a10c62dcac4c346eb0c4540a86e0921845738666b3
sha256sum $P | tee $O/binary.sha256
run() { local tag=$1; shift; $P selftest --netlist $N --pin $PIN "$@" > $O/$tag.txt 2>&1; echo "== $tag"; grep -h 'SELFTEST\|"pass":false\|panicked\|RT2\|^NEG' $O/$tag.txt | cut -c1-420; }
for s in b3 sha; do for n in 8 64; do run selftest-$s-$n --instances $I/inst-fp4-$s-$n.bin; done; done
if [ $PATCHED = 1 ]; then
  for c in fp4_root_flag_dropped fp4_tail_word_nonzero fp4_scale_block_forged_digest_only fp4_x_scale_operand_free_u5 fp4_x_scale_operand_free_u20 fp4_w_scale_operand_free_u7; do
    run neg-b3-$c --instances $I/inst-fp4-b3-8.bin --only $c
  done
  for c in sha_fp4_pad_marker_dropped sha_fp4_last_block_data_forged sha_fp4_scale_block_forged fp4_x_scale_operand_free_u5 fp4_x_scale_operand_free_u20 fp4_w_scale_operand_free_u7; do
    run neg-sha-$c --instances $I/inst-fp4-sha-8.bin --only $c
  done
fi
for f in fp4-b3-ytamper-8 fp4-sha-ytamper-8 fp4-b3-relabel-8; do run gap-$f --instances $I/inst-$f.bin --only honest; done
run gap-g2-honest-zero-scales --instances $I/inst-fp8shape-38383838-8.bin --only honest
if [ $PATCHED = 1 ]; then
  for s in 38383838 40404040; do run gap-g2-free-scale-$s --instances $I/inst-fp8shape-$s-8.bin --only free_scale_$s; done
fi
true
