#!/usr/bin/env bash
# red-team-flock-2: re-review of NV1–NV3 at flock-gpu-link 45fdab2d (on flock-backend 3d019e65), CPU only.
#  A. full selftests (the producer's cases + its admission negatives): Fp4, ShaFp4 (8, 12 VUs), Fp8, ShaFp8 (fp8-ada), Chunk(3) (bf16-hopper)
#  B. my rtf2 NVFP4 negatives again (the fp4 statement digest changed)
#  C. files admission must refuse (exit 2): my 0310Z gap files, fp8 out with a low bit, fp8 y committed unpacked
#  D. admitted files whose output was moved consistently (y and out): the proof must be refused
#  E. G4: the y tree's leaf width is the header's (u16 over a 22/32-bit output, u32 over a bf16 output)
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
sha256sum $P | tee $O/binary.sha256
pin() { case $1 in fp4-*) echo fb52a87c01a8a41f0e3460a10c62dcac4c346eb0c4540a86e0921845738666b3;; fp8-ada*) echo e66262a08816f03d7dba67860c68b3993adc9ca83f1746d15137b0b757599a7c;;
        bf16-hopper*|bf16h*) echo da1bbe2cdbf02971f0d7f12f6d5a3caabefb658af95afeeff44d001ff30dddba;; esac; }
net() { case $1 in *fp4*|*fp8shape*) echo net-fp4-nvf4.txt;; *fp8-ada*) echo net-fp8-ada.txt;; *bf16*) echo net-bf16-hopper.txt;; esac; }
run() {  # tag file [--only case]
  local tag=$1 f=$2; shift 2; local n; n=$(net $f)
  $P selftest --netlist $I/$n --pin $(pin ${n#net-}) --instances $I/$f "$@" > $O/$tag.txt 2>&1; local rc=$?
  echo "== $tag rc=$rc"; grep -h 'SELFTEST\|"pass":false\|REFUSED\|^NEG' $O/$tag.txt | cut -c1-360
}
for f in inst-fp4-b3-8 inst-fp4-sha-8 inst-fp4-b3-12 inst-fp8-ada-b3-8 inst-fp8-ada-sha-8 inst-bf16-hopper-b3-8; do run A-$f $f.bin; done
for c in fp4_root_flag_dropped fp4_tail_word_nonzero fp4_scale_block_forged_digest_only fp4_x_scale_operand_free_u5 fp4_x_scale_operand_free_u20 fp4_w_scale_operand_free_u7 fp4_dummy_block_forged; do
  f=inst-fp4-b3-8.bin; [ $c = fp4_dummy_block_forged ] && f=inst-fp4-b3-12.bin; run B-b3-$c $f --only $c
done
for c in sha_fp4_pad_marker_dropped sha_fp4_last_block_data_forged sha_fp4_scale_block_forged fp4_x_scale_operand_free_u5 fp4_w_scale_operand_free_u7; do run B-sha-$c inst-fp4-sha-8.bin --only $c; done
for f in inst-fp4-b3-ytamper-8 inst-fp4-sha-ytamper-8 inst-fp4-b3-relabel-8 inst-fp8shape-38383838-8 t-fp8-ada-b3-out_lowbit t-fp8-ada-sha-out_lowbit t-fp8-ada-b3-y_unpacked; do run C-$f $f.bin --only honest; done
for f in t-fp8-ada-b3-consistent_y_plus1 t-fp4-b3-consistent_y_plus1 t-bf16h-b3-consistent_y_plus1; do run D-$f $f.bin --only honest; done
for f in t-fp8-ada-b3-y_u16 t-fp4-b3-y_u16 t-bf16h-b3-y_u32_highbits; do run E-$f $f.bin --only honest; done
true
