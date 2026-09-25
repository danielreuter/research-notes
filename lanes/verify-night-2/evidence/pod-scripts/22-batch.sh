#!/usr/bin/env bash
# verify-night-2 09:40Z batch, /workspace/src = main 3301c435 (ligero-steps-pin merged: R1/R2/R4 in reverify, Rust layout_error):
# (0) rebuild ligero-verify from it (14, no pytest: verity/commitments unchanged since 00ffe398); (1) sp1-committed (19);
# (2) poseidon-v1 0925Z H100 BF16 / FP8 (plateaus first); (3) cross-check the two BLAKE3 cells with main's fixed reverify.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
I=$RESEARCH_RUN_DIR/inputs; W=/workspace/verify-night-2
[ -f /workspace/bin/ligero-verify-d89cffc7 ] || cp -p /workspace/bin/ligero-verify /workspace/bin/ligero-verify-d89cffc7
echo "=== [$(date -u +%H:%M:%S)] (0) rebuild ligero-verify @ $(python3 -c "import json;print(json.load(open('/workspace/src/.research-source.json'))['commit'][:8])")"
PYTEST=0 bash $I/14-rebuild.sh | grep -vE '^\s*$'
LV=$(sha256sum /workspace/bin/ligero-verify | cut -c1-8)
export VN2_VDESC="ligero-verify sha256 $LV (main 3301c435)"
echo "verifier: $VN2_VDESC"
echo "=== [$(date -u +%H:%M:%S)] (1) sp1-committed"
LABEL=1 bash $I/19-sp1c-verify.sh | grep -E '^(===|statement|proof|tampered|my roots|dump|vk|honest|wrong|tampered|proof-byte|other|batch|GATE|label|set file|flipped)' | cut -c1-500
PV="Producer poseidon-v1 (tree lane/poseidon-v1 82adc8a7 = main 94b1c4d2 + the hash-commit --commit-reps harness; prover-side; verified here with main 3301c435's verifier + reverify). Negatives (05, my verifier): proof byte, chain-end stmt byte, swapped stmts REJECT; base ACCEPT."
SYN="synthetic instances (the relation has no frozen tier past 4096): statements bound to my tree's relchain.instances(rel, N), whose first 4096 VUs equal the 4096 set the published n = 4096 cells bind"
echo "=== [$(date -u +%H:%M:%S)] (2a) H100 BF16 plateau n 32768"
TAG=h100-bf16-32768 VN2_N=32768 LABEL=1 PV_NOTE="$PV n = 32768: $SYN." bash $I/20-cells.sh \
  art:7d835b9a936c328b33ef09a992918b43a03c7d6680fe6b4f27be95523f7cb79e -- art:72e2b0ba613a9eec4ca4fc8b71024b20d4185a774764702cda436881c02191b9
echo "=== [$(date -u +%H:%M:%S)] (2b) H100 FP8 plateau n 65536"
TAG=h100-fp8-65536 VN2_N=65536 LABEL=1 PV_NOTE="$PV n = 65536: $SYN." bash $I/20-cells.sh \
  art:29a6bee71ac95928ba557b3f0c37c2e3ca4332a71f92aa321f14c8f1e3ac3fd0 -- art:23528a63b8129a46becc23d82ec9191690bf4ae372ba4e38770365a7e639a482
echo "=== [$(date -u +%H:%M:%S)] (2c) H100 n 4096 x2"
TAG=h100-4096 VN2_N=4096 LABEL=1 PV_NOTE="$PV" bash $I/20-cells.sh \
  art:08487b4a13190f45f9c89c96b635599378d4542ea5490e70f7293fdd770ea3c0 art:3e601d7162986162082f1317ee11b965caee4c2bc071e5e42967aa9bb862bf78 -- \
  art:f25486f62a49570c9e13013b1683d19e6f51680cfdae0ea4fed874c02fc3d4d0 art:6c512437a8fa5e57bc860a723edd0ecbacf4f0e61820944b78e349d327aa8853
echo "=== [$(date -u +%H:%M:%S)] (3) BLAKE3 cells, main 3301c435's reverify (R1/R2/R4 built in), dry-run cross-check"
mkdir -p $W/b3-xcheck
$PY -m backends.direct.ligero.reverify art:5d20ad00f5e7b251987cfc58998199e7c8ee8e35fd935d9a0c9dfb5ad1853a40 art:d6328cf5ef00648038cb35a171f212ee39a9d5f341c1f049ce4a7eb1671f874e \
  --dry-run --verifier /workspace/bin/ligero-verify --jobs 16 --work $W/b3-xcheck/rv 2>&1 | grep -vE '^\s*$' | tail -12
rm -rf $W/b3-xcheck/rv
echo "=== [$(date -u +%H:%M:%S)] 22 done"
