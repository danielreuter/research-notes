#!/usr/bin/env bash
# red-team-flock-3: PR #87 (flock-gpu-link @ 28f55d9a) at ul = 14, CPU, local build (the verifier untouched in both binaries).
#   pr87_tests.sh DIR   (DIR: net-*.txt, inst-*.bin; binaries under /tmp/rtf3/bin-{main,pr87})
set -uo pipefail
D=$1; PM=/tmp/rtf3/bin-main/flock-pure-gpu; P=/tmp/rtf3/bin-pr87/flock-pure-gpu; PR=/tmp/rtf3/bin-pr87/flock-pure-gpu.rt3
echo "binaries: main $(sha256sum $PM | cut -c1-16) pr87 $(sha256sum $P | cut -c1-16) pr87+rt3 $(sha256sum $PR | cut -c1-16)"
st() {  # tag bin net inst [args]
  local tag=$1 b=$2 n=$3 f=$4; shift 4
  $b selftest --netlist $D/$n --instances $D/$f "$@" > $D/$tag.txt 2>&1; local rc=$?
  echo "== $tag rc=$rc $(grep -h '^SELFTEST\|REFUSED' $D/$tag.txt | head -1 | cut -c1-230) pass=$(grep -c '"pass":true' $D/$tag.txt) fail=$(grep -c '"pass":false' $D/$tag.txt)"
  grep -h '"pass":false' $D/$tag.txt | cut -c1-250
}
# 1. the producer's selftest with the total unit (ul 14)
st S14-chunk4 $P net-bf16-ampere-total.txt inst-bf16-chunk4-8.bin
st S14-chunktail4 $P net-bf16-ampere-total.txt inst-bf16-chunktail4-8.bin
st S14-chunk16 $P net-bf16-ampere-total.txt inst-bf16-chunk16-8.bin
# 2. regression: the finite 2^13 unit, PR and main
st S13-pr87-chunk4 $P net-bf16-ampere.txt inst-bf16-chunk4-8.bin
st S13-main-chunk4 $PM net-bf16-ampere.txt inst-bf16-chunk4-8.bin
# 3. my flips at ul 14 (each must be refused): padding rows, the last slot's last bit, the constant row, rows past 2^13
for fl in 9000:5 12000:16 16383:31 8448:31 8200:0 700:31; do
  RT3_UNIT_FLIP=$fl st F14-chunk4-${fl/:/-u} $PR net-bf16-ampere-total.txt inst-bf16-chunk4-8.bin --only unit_internal_bit_flipped
  grep -ho '"accepted":[a-z]*\|"reps_ok":[^]]*\][^]]*\]\]' $D/F14-chunk4-${fl/:/-u}.txt | tr '\n' ' '; echo
done
for fl in 9000:15 16383:31; do
  RT3_UNIT_FLIP=$fl st F14-chunktail4-${fl/:/-u} $PR net-bf16-ampere-total.txt inst-bf16-chunktail4-8.bin --only unit_internal_bit_flipped
  grep -ho '"accepted":[a-z]*\|"reps_ok":[^]]*\][^]]*\]\]' $D/F14-chunktail4-${fl/:/-u}.txt | tr '\n' ' '; echo
done
# 4. UL1 at admission: the total unit on a SHA-leaf bf16 file (must be refused), the finite unit on it (admitted)
if [ -f $D/inst-bf16-sha-k1536-8.bin ]; then
  st UL1-total-sha $P net-bf16-ampere-total.txt inst-bf16-sha-k1536-8.bin --only honest
  st UL1-finite-sha $P net-bf16-ampere.txt inst-bf16-sha-k1536-8.bin --only honest
fi
true
