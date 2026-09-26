#!/usr/bin/env bash
B=/tmp/rtf3/fb/flock/target/release/flock-ir-frame; O=$HOME/.research/runs/r20260926-132829-2165/out; F129=/tmp/rtf3/files/cap-t129/frame-4.bin; N129=/tmp/rtf3/files/cap-t129/net.txt; M=/tmp/rtf3/class/class-129-256.json
echo "binary $(sha256sum $B | cut -c1-16) source $(git -C /tmp/rtf3-srcE log -1 --format=%h)"
for c in whitespace duplicate_129 missing_t200 extra_t257; do $B loadcheck --instances $F129 --netlist $N129 --class $O/$c.json --pin $(sha256sum $O/$c.json | cut -c1-64) --tables /tmp/rtf3/tables > /tmp/cp2-$c.txt 2>&1; echo "== CP2 $c want=2 rc=$? $(grep -h REFUSED /tmp/cp2-$c.txt | cut -c1-160)"; done
$B loadcheck --instances $F129 --netlist $N129 --class $M --pin $(sha256sum $M | cut -c1-64) --tables /tmp/rtf3/tables > /tmp/cp2-honest.txt 2>&1; echo "== CP2 honest want=0 rc=$?"
