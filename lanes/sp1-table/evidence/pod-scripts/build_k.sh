#!/bin/bash
# sp1-table (pod): build the relation-bare CUDA host from /workspace/src as variant TAG, keep its guest ELF and the
# check_vu disassembly, and compare it on the executor (indexed layout, all 4096 VUs).
#   build_k.sh k5    (writes /workspace/bin/veritor-zk-host-cuda-relation-bare-k5, guest-k5.elf, check_vu_k5.s)
set -e
TAG=$1
source ~/.cargo/env
cd /workspace/src/backends/sp1
CARGO_TARGET_DIR=/workspace/sp1-target-cuda-relation-bare cargo build --release --locked -p veritor-zk-host \
  --features cuda,relation-bare 2>&1 | tail -6 > /workspace/sp1-table/build-$TAG.log
cp /workspace/sp1-target-cuda-relation-bare/release/veritor-zk-host /workspace/bin/veritor-zk-host-cuda-relation-bare-$TAG
cp /workspace/sp1-target-cuda-relation-bare/elf-compilation/riscv64im-succinct-zkvm-elf/release/veritor-zk-guest /workspace/sp1-table/guest-$TAG.elf
OBJDUMP=$(ls ~/.sp1/toolchains/*/lib/rustlib/*/bin/llvm-objdump 2>/dev/null | head -1)
if [ -n "$OBJDUMP" ]; then
  $OBJDUMP -d -C --no-show-raw-insn /workspace/sp1-table/guest-$TAG.elf > /workspace/sp1-table/guest-$TAG.s
  awk 'BEGIN{p=0} /^[0-9a-f]+ <[^.].*>:$/{ if (p) exit; if ($0 ~ /bare::check_vu>:/) p=1 } p' \
    /workspace/sp1-table/guest-$TAG.s > /workspace/sp1-table/check_vu_$TAG.s
  echo "check_vu: $(wc -l < /workspace/sp1-table/check_vu_$TAG.s) lines"
fi
sha256sum /workspace/sp1-table/guest-$TAG.elf
HI=4096 EXTRA="--layout indexed" TAG=idx /workspace/sp1-table/exec_cmp.sh veritor-zk-host-cuda-relation-bare-$TAG
