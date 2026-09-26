#!/usr/bin/env bash
# agkr-real-k: 30-gate-cells.sh on both registered cells (art:95fdd0ae K = 2048 at 2,048 VUs; art:20197f8b K = 8192 at 512 VUs),
# from the store, with this tree's verity-gkr-verify and flock-link (b684b12 + both patches + backends/flock/live).
#   VB=... FL=... bash 31-gate-both.sh
set -uo pipefail
RD=${RESEARCH_RUN_DIR:?}; T=$HOME/.research/store/trees; G=$(dirname "$0")/30-gate-cells.sh
for a in art:b7b5298a art:eb4977b8 art:8455c116 art:05aa00b9 art:c2b10a12 art:15e93b91; do research data fetch $a > /dev/null || exit 1; done
sha256sum $VB $FL | tee $RD/binaries.sha256
bash $G $T/b7b5298afe736ae265de09f7551676ff676dde7eaeb1fcf3c3c05d16526a8f78 $T/eb4977b859aeef42f68d0b432cfdc267177c42315b81a0517e3d1c7d1b657b79 \
  $T/8455c11603940e9a99d8b9da82284bbde0425038670d8835689234d78c52bb0f 2048 bf16-ampere-k2048+blake3 $VB $FL $RD/gates
bash $G $T/05aa00b9444a95c7c19c86fa8f37e72e5d8ff29e28b46bd30de386998ea259e3 $T/c2b10a127eb5dbce528e86445b7415633bb0619cc7a93bc94d8fc3aa8ef91046 \
  $T/15e93b9173d405fb027c115fe5cb0bbe1cbd41d95b4759c3105a86c8e898031a 512 bf16-ampere-k8192+blake3 $VB $FL $RD/gates
find $RD/gates -name '*.bin' -delete
