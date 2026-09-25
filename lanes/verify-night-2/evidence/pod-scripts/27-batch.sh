#!/usr/bin/env bash
# verify-night-2 11:40Z batch, /workspace/src = main bfb0b928 (PR #21: bench / instance_equiv only; ligero-verify source as 767115db,
# binary 8941c72d from 25): b-ligero-standard-hash's malloc-env re-measurements (1037Z) and the x1 16384 plateau (1125Z).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
I=$RESEARCH_RUN_DIR/inputs
LV=$(sha256sum /workspace/bin/ligero-verify | cut -c1-8)
export VN2_VDESC="ligero-verify sha256 $LV (main bfb0b928; ligero-verify source unchanged since 767115db)"
echo "verifier: $VN2_VDESC"
FN="file re-verification (runner's coins), not transferable."
SYN="synthetic instances (no frozen tier past 4096): statements bound to my tree's relchain.instances(rel, N), whose first 4096 VUs equal the frozen 4096 set"
BL="Producer b-ligero-standard-hash (tree 806a2f73, GPU committer, malloc env set); verified with main bfb0b928's verifier + reverify. $FN"
echo "=== [$(date -u +%H:%M:%S)] (1) fp8-ada+blake3 4096 (1037Z)"
TAG=4090-b3m-4096 VN2_N=4096 LABEL=1 PV_NOTE="$BL" bash $I/20-cells.sh \
  art:0c5840907e1c24fe8190d0af2b0e32763494ba413b939e0b8d8cf9195f569b4e -- art:9b80f566838f4956ecc85df853c718ddfe07a5af8682dd69f29b3c7df75ae611
echo "=== [$(date -u +%H:%M:%S)] (2) fp8-ada+blake3 16384 plateau (1125Z; not converged: 32768 OOM, +3.06 % over 4096)"
TAG=4090-b3m-16384 VN2_N=16384 LABEL=1 PV_NOTE="$BL n = 16384: $SYN. Producer caveat: the sweep did not converge (32768 point OOM-killed; +3.06 % over 4096 misses the < 2 % rule): highest measured point, not a converged plateau." bash $I/20-cells.sh \
  art:443b52fd8c9a4ace5e31d7d263a01d719eb44d67576f3168d31d0e5f067feb67 -- art:c9f4a645c2271c64187a2d2e8d116a5c34b0f465c9fd4ddc333d4ce7887dec1d
echo "=== [$(date -u +%H:%M:%S)] (3) fp8-ada-x4+blake3 4096 (1037Z)"
TAG=4090-b3mx4-4096 VN2_N=4096 LABEL=1 PV_NOTE="$BL" bash $I/20-cells.sh \
  art:ef264ad325e8207dae1b75b2d09b35d13cfbfe1b1c717bc40592afd69043df62 -- art:050ddede1083ac67f417d2345d5b1f0a8d47314c94ee5a9988d7f1cdb8300650
echo "=== [$(date -u +%H:%M:%S)] (4) fp8-ada-x4+blake3 8192 plateau (1037Z)"
TAG=4090-b3mx4-8192 VN2_N=8192 LABEL=1 PV_NOTE="$BL n = 8192: $SYN." bash $I/20-cells.sh \
  art:a3d4b768d9808c55be90c98bd54fa10b5dd993faec8e2cb90a622bd912862e3a -- art:19be6afa2cd2239cf15f7878af8eae0a3523be86dbec8e92f3acd9d6ee3ebbd1
echo "=== [$(date -u +%H:%M:%S)] 27 done"
