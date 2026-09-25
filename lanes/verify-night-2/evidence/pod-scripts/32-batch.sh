#!/usr/bin/env bash
# verify-night-2 12:20Z batch, /workspace/src = main 2c92b9e3 (the bf16-hopper-x4+sha256 PINS row; diff bfb0b928..2c92b9e3 reviewed:
# one leaf.rs row + views / tables / research-tool code). Disk: after each group, head-verify its trees in the runner store (so they
# are evictable), evict to 30 GB free, and drop the negatives' tree copies (summaries kept).
#   (0) rebuild ligero-verify; (1) blake3-80gb 1210Z preferred four (1f36a20a); (2) +sha256 x4: fp8-hopper 32768, bf16-hopper 8192;
#   (3) poseidon-v1 H100 malloc plateaus 32768 x2; (4) blake3-80gb 75cbbac1 four; (5) poseidon-v1 H100 4096 x2 + A100 4096.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
I=$RESEARCH_RUN_DIR/inputs; W=/workspace/verify-night-2
C=$(python3 -c "import json;print(json.load(open('/workspace/src/.research-source.json'))['commit'][:8])")
room() {
  ( export RESEARCH_STORE=/workspace/research/store
    for t in "$@"; do $PY -m research data push $t --verify head 2>&1 | grep -c PRESERVED | sed "s|^|  head-verified ${t:0:12}: |"; done
    $PY -m research data evict --target-free-gb 30 2>&1 | tail -1 )
  for d in $W/neg-*; do [ -f $d/summary.txt ] && find $d -mindepth 1 -maxdepth 1 ! -name summary.txt -exec rm -rf {} +; done
  df -h / | tail -1
}
room $(cat $I/vn2-arts.txt)
[ -f /workspace/bin/ligero-verify-8941c72d ] || cp -p /workspace/bin/ligero-verify /workspace/bin/ligero-verify-8941c72d
echo "=== [$(date -u +%H:%M:%S)] (0) rebuild ligero-verify @ $C"
PYTEST=0 bash $I/14-rebuild.sh | grep -vE '^\s*$' | tail -8
LV=$(sha256sum /workspace/bin/ligero-verify | cut -c1-8)
export VN2_VDESC="ligero-verify sha256 $LV (main $C)"
echo "verifier: $VN2_VDESC"
FN="file re-verification (runner's coins), not transferable."
SYN="synthetic instances (no frozen tier past 4096): statements bound to my tree's relchain.instances(rel, N), whose first 4096 VUs equal the frozen 4096 set"
B3="Producer blake3-80gb (re-registered proofs/ trees, run r20260925-114945-d8d5, hard-linked, no re-proving)"
B3P="$B3; measured on 1f36a20a = main 767115db (r20260925-105424-0095); verified with main $C's verifier + reverify. $FN"
B3O="$B3; measured on 75cbbac1 = main 3301c435 (r20260925-095924-a6ec); verified with main $C's verifier + reverify. $FN"

echo "=== [$(date -u +%H:%M:%S)] (1) blake3-80gb preferred: 4096 x2"
T1="art:29a5f05fa40d4ac37d931c492444a848d8e3d166992f0717b810e086739ce1bc art:19ff3bfee92372f9f8571b28dbd4f8481d2bb1eb4ff893d8523e3868f342560c"
TAG=h100b3p-4096 VN2_N=4096 LABEL=1 PV_NOTE="$B3P" bash $I/20-cells.sh $T1 -- \
  art:c87305748221538ea25932474c74897a56bb2998db8b71e815d89ad890fb113f art:9c11326c5fcd7cce3c4d882675268e80e9c463e69b145fe40ad9bca4c6e06103
echo "=== [$(date -u +%H:%M:%S)] (1b) blake3-80gb preferred: bf16-hopper 16384 plateau"
TAG=h100b3p-16384 VN2_N=16384 LABEL=1 PV_NOTE="$B3P n = 16384: $SYN." bash $I/20-cells.sh \
  art:7c89085f515db5fa5fcc314fd9c5f7c1e7f3f2002c5591c0cf6987f3958661a8 -- art:7c6b46478627c6da59d91165be9a8060c8840a19dc54be309eba03e8ab23c655
echo "=== [$(date -u +%H:%M:%S)] (1c) blake3-80gb preferred: fp8-hopper 32768 plateau"
TAG=h100b3p-32768 VN2_N=32768 LABEL=1 PV_NOTE="$B3P n = 32768: $SYN." bash $I/20-cells.sh \
  art:3d235ab605f10d02eeb6231e68d0cbdb61521d4b69e3150d4b06e6ddb25b3323 -- art:7a3965da4d11460b47a19707fb870de36c8e7cdb5e42818014a579e0df13eec5
room $T1 art:7c89085f515db5fa5fcc314fd9c5f7c1e7f3f2002c5591c0cf6987f3958661a8 art:3d235ab605f10d02eeb6231e68d0cbdb61521d4b69e3150d4b06e6ddb25b3323

SH="Producer b-ligero-sha256 (H100, malloc env set); verified with main $C's reverify + ligero-verify (sha256 scheme as merged at 767115db; bf16-hopper-x4+sha256 PINS row at 2c92b9e3). $FN"
echo "=== [$(date -u +%H:%M:%S)] (2a) +sha256 fp8-hopper-x4 32768 plateau (run at da74b03e)"
TAG=h100sh-x4-32768 VN2_N=32768 LABEL=1 PV_NOTE="$SH Run r20260925-095503-e592 at da74b03e. n = 32768: $SYN." bash $I/20-cells.sh \
  art:61842848ecbed86882d4f806bfbfb09bbb84634b040b5bfbc5c2892ec9a914d7 -- art:4aa258eeba99ce7da2e2c43b9068530cab43c8f3e8907ebc59610e71db9cad84
room art:61842848ecbed86882d4f806bfbfb09bbb84634b040b5bfbc5c2892ec9a914d7
echo "=== [$(date -u +%H:%M:%S)] (2b) +sha256 bf16-hopper-x4 8192 plateau (run at b009fdc8)"
TAG=h100sh-bx4-8192 VN2_N=8192 LABEL=1 PV_NOTE="$SH Run r20260925-113022-5a5f at b009fdc8. n = 8192: $SYN." bash $I/20-cells.sh \
  art:c25cac59f2a79ef887bac732f74725d9cb65690e47a2611f168ab24e072b5f9f -- art:fcd6a623afad79183167c6019876da71614db8a8b820f9eb102ea28a6ed87af4
room art:c25cac59f2a79ef887bac732f74725d9cb65690e47a2611f168ab24e072b5f9f

PV="Producer poseidon-v1 (tree lane/poseidon-v1 7ffb7095 = main 3301c435 + the hash-commit --commit-reps harness, malloc env set); verified with main $C's verifier + reverify. Negatives (05, my verifier): proof byte, chain-end stmt byte, swapped stmts REJECT; base ACCEPT."
echo "=== [$(date -u +%H:%M:%S)] (3) poseidon-v1 H100 malloc plateaus 32768 x2"
T3="art:5838a96fece25aba323495c4dbc995c5cd0c4d28e6415d34d9b2ed34f39e31df art:6916a8dd9cc042be12dcae836528c6c64c6390617b1131b8a048d35952d98d16"
TAG=h100m-32768 VN2_N=32768 LABEL=1 PV_NOTE="$PV H100 run r20260925-104045-de31. n = 32768: $SYN." bash $I/20-cells.sh $T3 -- \
  art:a250d4b79a061a1143b6549512850a756c011b014d438a2ac0caf00a942fc9f6 art:752dcde9e0bdef860712dba417e43fd511a78a2d6a4edaff54dae84a47062394
room $T3

echo "=== [$(date -u +%H:%M:%S)] (4) blake3-80gb 75cbbac1: 4096 x2, bf16 8192, fp8 16384"
T4="art:70ca2a6950b944487458a7d87933dc64b3994398ac10fec28bfb19dbdfe74c2a art:c808b8b0e89886e441180bd758c23f81c03cf1ec1749accb281f22c289126bf3"
TAG=h100b3o-4096 VN2_N=4096 LABEL=1 PV_NOTE="$B3O" bash $I/20-cells.sh $T4 -- \
  art:d33257bbc7d15eb1245fb881754305cd288daf77b4bcbd8880f766ac998ef421 art:41f7727f5f66a5171eafc3edbeb6b8b7e5ebbb2b376f275d948bf75f63b861c1
TAG=h100b3o-8192 VN2_N=8192 LABEL=1 PV_NOTE="$B3O n = 8192: $SYN." bash $I/20-cells.sh \
  art:b7dba6111035e38da4f49a6adbb18e9f0858538eb327f75a4b84a2f74a1dd768 -- art:a36d1405b6d93ab9591b5092c901d001ac0514d352a62bd8f133c7e38a9319b2
TAG=h100b3o-16384 VN2_N=16384 LABEL=1 PV_NOTE="$B3O n = 16384: $SYN." bash $I/20-cells.sh \
  art:0d9fe4cd2b7b2fec4c017e7a166b4af771f8ed1b13c24fb1ea0c4c562928485a -- art:1ea7c3590d9c0ab513f752fc0a118e93ace0917462db01d714aa122a5f5c8c51
room $T4 art:b7dba6111035e38da4f49a6adbb18e9f0858538eb327f75a4b84a2f74a1dd768 art:0d9fe4cd2b7b2fec4c017e7a166b4af771f8ed1b13c24fb1ea0c4c562928485a

echo "=== [$(date -u +%H:%M:%S)] (5) poseidon-v1 H100 4096 x2 + A100 4096"
TAG=h100m-4096 VN2_N=4096 LABEL=1 PV_NOTE="$PV H100 run r20260925-104045-de31." bash $I/20-cells.sh \
  art:0c45644d9a1a8e7d4648e085a6416f5db220a0dd644b38fb5f2869e9507397b7 art:9a2f94e0c49653f1ab71eeadc798878d6eca4e80da3eaf51d89eb9f2f7f662b3 -- \
  art:a4499799122f6831407f41cb63d166e504ffc6ff24e3f5a4de6508151fbb26bb art:279b8685af35d3850fd020fa9e6ae65ba3009d1e6434ac61990c654659ba43f5
TAG=a100m-4096 VN2_N=4096 LABEL=1 PV_NOTE="$PV A100 (1205Z handoff), sweep bounded by the frozen set." bash $I/20-cells.sh \
  art:5eb0b2cc73fb55da05902920afe9d7467d330e3036312b0c890588e7935ce320 -- art:ba387d41cb12945914624f0cbdabb4b3a8ffc2675779e1f7f17cc6dea8840f07
room art:0c45644d9a1a8e7d4648e085a6416f5db220a0dd644b38fb5f2869e9507397b7 art:9a2f94e0c49653f1ab71eeadc798878d6eca4e80da3eaf51d89eb9f2f7f662b3 art:5eb0b2cc73fb55da05902920afe9d7467d330e3036312b0c890588e7935ce320
echo "=== [$(date -u +%H:%M:%S)] 32 done"
