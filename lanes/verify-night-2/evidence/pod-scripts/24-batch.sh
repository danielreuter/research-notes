#!/usr/bin/env bash
# verify-night-2 10:40Z batch, /workspace/src = main 3301c435, ligero-verify sha256 596529d2: poseidon-v1 1030Z RTX 5090 NVFP4
# (fp4-nvf4+poseidon2, alg.) n 4096 art:70f275ac, then the n 131072 plateau art:6740eb22 (385 sub-batches).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
I=$RESEARCH_RUN_DIR/inputs
LV=$(sha256sum /workspace/bin/ligero-verify | cut -c1-8)
export VN2_VDESC="ligero-verify sha256 $LV (main 3301c435)"
echo "verifier: $VN2_VDESC"
PV="Producer poseidon-v1 (tree lane/poseidon-v1 82adc8a7 = main 94b1c4d2 + the hash-commit --commit-reps harness; RTX 5090 run r20260925-101124-095a); verified with main 3301c435's verifier + reverify. Negatives (05, my verifier): proof byte, chain-end stmt byte, swapped stmts REJECT; base ACCEPT."
SYN="instances past the frozen 4096: statements bound to my tree's relchain.instances(fp4-nvf4, N), whose first 4096 VUs equal the frozen NVFP4 set"
echo "=== [$(date -u +%H:%M:%S)] (1) 5090 NVFP4 +hash 4096"
TAG=5090-fp4-4096 VN2_N=4096 LABEL=1 PV_NOTE="$PV" bash $I/20-cells.sh \
  art:d8a0d85687882ff6bd91a321b439161dc196447c44191153b07b527e1a39826e -- art:70f275ac21a3da6073c261b1981dd3dd7f253af204f25efd63fe7a780ebb7a33
echo "=== [$(date -u +%H:%M:%S)] (2) 5090 NVFP4 +hash plateau 131072"
df -h /workspace | tail -1
TAG=5090-fp4-131072 VN2_N=131072 LABEL=1 PV_NOTE="$PV n = 131072: $SYN." bash $I/20-cells.sh \
  art:dcef74f10d47802138ccf4346da3c1d9966e3a4398188e0d990aae2249522b39 -- art:6740eb223e1442f94794860282ae04e8b9579163c262c7348fa2334fee5bd23a
echo "=== [$(date -u +%H:%M:%S)] 24 done"
