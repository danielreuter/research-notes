#!/usr/bin/env bash
# verify-night-3 round 2 (coordinator 1940Z/1945Z): bootstrap, then equiv regen/compare x3 (+ vllm tree), then reverify x3
I=$(dirname "$0")
BENCH_INSTANCES=1 HEALTH=0 bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh > /workspace/bootstrap.log 2>&1; grep -E "FAILED|BOOTSTRAP" /workspace/bootstrap.log | tail -3
A=art:dc455fc8d022da8059964d26cf1a977f2dd3b834a1181c7138bc0567b0f6a79b; B=art:40b23d0b725c0773540f4c906d809c1972d7d8ad718a21f326d961e2dcdcfd5e
C=art:d4402d29587bb6d39a7d3d5411e4bcde828a74fada14ab83254e22f66cf0e50f
RA=art:ac1f532cbaf6a172098582249194d6fefb1adb7a9810628fd577f0adc14c7457; RB=art:675a03a34359589d675557592554665f570e7785736303ce69d7110bc8a706fe
RC=art:f7aac95f5750d26638c68e38c2464259affe08ac5ec767b46de3ac1e415be7be
echo "## equiv"
bash $I/41-regen.sh /workspace/src $A fp8-ada-x4 16384 $RA
bash $I/41-regen.sh /workspace/src $B bf16-ampere-x4 4096 $RB
bash $I/41-regen.sh /workspace/src-vllm $C fp8-ada-x4 16384 $RC
bash $I/41-regen.sh /workspace/src $C fp8-ada-x4 16384
echo "## reverify"
bash $I/42-reverify-tree.sh /workspace/src $RB $RA
bash $I/42-reverify-tree.sh /workspace/src-vllm $RC
echo ROUND2_DONE
