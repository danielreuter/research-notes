#!/usr/bin/env bash
# verify-night-2 09:10Z batch: (1) b-ligero-standard-hash 0905Z fp8-ada+blake3 cells (priority), (2) poseidon-v1 relabels
# (0800Z / 0835Z / 0900Z; checks passed in r20260925-084940-2e1f, labels refused there by the old 11-label guard; negatives
# reused), (3) the sp1-committed host build (18, STAGE=build) for the 0850Z coordinator request.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
I=$RESEARCH_RUN_DIR/inputs
SH="Producer b-ligero-standard-hash (lane/b-ligero-standard-hash d5b299ff / dc2cae87; verifier-side diff vs main reviewed: R1 layout_error refusals, 2 other-device pins, v6 K check; prover-side leaf_bytes_many). Verified with main's verifier plus my own R1/R2/R4 core checks, not the producer's reverify. Negatives (05, my verifier): proof byte, chain-end stmt byte, swapped stmts REJECT; base ACCEPT."
PV="Producer poseidon-v1 (tree lane/poseidon-v1 54ad119d = main + hash-commit harness 6e1cc576 + committer b862be30, prover-side only; verified here with main's verifier). Negatives (05, my verifier, run r20260925-084940-2e1f): proof byte, chain-end stmt byte, swapped stmts REJECT; base ACCEPT."
BEYOND="whose first 4096 VUs equal the frozen set; whether such a point enters the tables is the renderer's call."
echo "=== [$(date -u +%H:%M:%S)] (1a) blake3 4096"
TAG=b3-4096 VN2_N=4096 LABEL=1 PV_NOTE="$SH" bash $I/20-cells.sh \
  art:3e64461f92030cafa89f8260f83d0260b6c5856fd74c1a49c094fc79ba065310 -- art:5d20ad00f5e7b251987cfc58998199e7c8ee8e35fd935d9a0c9dfb5ad1853a40
echo "=== [$(date -u +%H:%M:%S)] (1b) blake3 16384 plateau"
TAG=b3-16384 VN2_N=16384 LABEL=1 PV_NOTE="$SH n = 16384 > the 4096-VU frozen tier: statements are bound to my tree's relchain.instances(fp8-ada, 16384) (synthetic recipe continued, n-keyed digest), $BEYOND" bash $I/20-cells.sh \
  art:0269046e49e47beda0cf6801812669f0628f8608236a1d5ce3d9234b6f065c77 -- art:d6328cf5ef00648038cb35a171f212ee39a9d5f341c1f049ce4a7eb1671f874e
echo "=== [$(date -u +%H:%M:%S)] (2a) poseidon-v1 4096 relabel (+ art:af008992, same tree as art:289841b1)"
TAG=pv4096 VN2_N=4096 LABEL=1 NEG=0 PV_NOTE="$PV" bash $I/20-cells.sh \
  art:c24671eeec267cb82ce2ca50cd361329844554f79491469b1150536c69f241cb art:decbf2b3b9e88de6943cb99e8f058eb4352f2f894019bf0aa569eb56ed365a8f -- \
  art:d87b4895ff9817b9bd9120a8c39a1740c009e49aab569b5a1cbc130f4e7e6ffd art:af0089920b38b6e8c7dd2d51c93da51ee2e93abd4ee479880b8027b9113ab1ad \
  art:289841b1075e0fc56450cce92109fd6edc84c3dd594515d8b47a37953a06c6a4
echo "=== [$(date -u +%H:%M:%S)] (2b) poseidon-v1 32768 relabel"
TAG=pv32768 VN2_N=32768 LABEL=1 NEG=0 PV_NOTE="$PV n = 32768 > the 4096-VU frozen tier: statements are bound to my tree's relchain.instances(rel, 32768) (fp8-ada: synthetic recipe continued; bf16-ampere: frozen ids recycled i mod 4096; bench.views reason I per poseidon-v1 0900Z), $BEYOND" bash $I/20-cells.sh \
  art:30f6e8db1871cf1c94ec0c93b55b61d3d8af7b33b33ef58ba0a477392b37d232 art:da6298bf6820c12bb8a2bb72f9115a59079635b33fd7facdae98754232efb905 -- \
  art:c8b52ee221d292132655a3b9000660e4ea6151da376be6ef2f248f830c8ecd54 art:b5a4454f754fe0609ed888c93a8386915b243ad0281521049dab42108189b4d7
echo "=== [$(date -u +%H:%M:%S)] (3) sp1-committed host build"
STAGE=build bash $I/18-sp1c-build.sh | tail -30
echo "=== [$(date -u +%H:%M:%S)] 21 done"
