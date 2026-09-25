#!/usr/bin/env bash
# verify-night-2 11:55Z batch, /workspace/src = main bfb0b928 (ligero-verify 8941c72d; source unchanged since 767115db, which carries
# the sha256 leaf scheme): (1) b-ligero-sha256 1150Z fp8-hopper-x4+sha256 32768 plateau (run at da74b03e); (2) poseidon-v1 1150Z
# H100 malloc re-measurements: plateaus bf16-hopper / fp8-hopper 32768, then the two 4096 points.
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
echo "=== [$(date -u +%H:%M:%S)] (1) H100 fp8-hopper-x4+sha256 plateau 32768"
SH="Producer b-ligero-sha256 (tree da74b03e, in main 767115db; H100 run r20260925-095503-e592, malloc env set); verified with main bfb0b928's reverify + ligero-verify (the sha256 scheme as merged at 767115db). $FN"
TAG=h100-sh-x4-32768 VN2_N=32768 LABEL=1 PV_NOTE="$SH n = 32768: $SYN." bash $I/20-cells.sh \
  art:61842848ecbed86882d4f806bfbfb09bbb84634b040b5bfbc5c2892ec9a914d7 -- art:4aa258eeba99ce7da2e2c43b9068530cab43c8f3e8907ebc59610e71db9cad84
PV="Producer poseidon-v1 (tree lane/poseidon-v1 7ffb7095 = main 3301c435 + the hash-commit --commit-reps harness; H100 run r20260925-104045-de31, malloc env set); verified with main bfb0b928's verifier + reverify. Negatives (05, my verifier): proof byte, chain-end stmt byte, swapped stmts REJECT; base ACCEPT."
echo "=== [$(date -u +%H:%M:%S)] (2a) H100 bf16-hopper+hash / fp8-hopper+hash plateaus 32768"
TAG=h100m-32768 VN2_N=32768 LABEL=1 PV_NOTE="$PV n = 32768: $SYN." bash $I/20-cells.sh \
  art:5838a96fece25aba323495c4dbc995c5cd0c4d28e6415d34d9b2ed34f39e31df art:6916a8dd9cc042be12dcae836528c6c64c6390617b1131b8a048d35952d98d16 -- \
  art:a250d4b79a061a1143b6549512850a756c011b014d438a2ac0caf00a942fc9f6 art:752dcde9e0bdef860712dba417e43fd511a78a2d6a4edaff54dae84a47062394
echo "=== [$(date -u +%H:%M:%S)] (2b) H100 4096 x2"
TAG=h100m-4096 VN2_N=4096 LABEL=1 PV_NOTE="$PV" bash $I/20-cells.sh \
  art:0c45644d9a1a8e7d4648e085a6416f5db220a0dd644b38fb5f2869e9507397b7 art:9a2f94e0c49653f1ab71eeadc798878d6eca4e80da3eaf51d89eb9f2f7f662b3 -- \
  art:a4499799122f6831407f41cb63d166e504ffc6ff24e3f5a4de6508151fbb26bb art:279b8685af35d3850fd020fa9e6ae65ba3009d1e6434ac61990c654659ba43f5
echo "=== [$(date -u +%H:%M:%S)] 30 done"
