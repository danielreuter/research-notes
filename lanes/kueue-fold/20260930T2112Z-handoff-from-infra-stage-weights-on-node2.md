---
id: 20260930T2112Z-handoff-from-infra-stage-weights-on-node2
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# kueue-fold: stage Mistral-7B and Qwen3-30B-A3B weights on node 2 so circuits' Builds stop failing there; publish the list of staged models

Six `verity-build-cov-*` Builds failed on node 2 because those weights aren't staged: about 15 GB and 61 GB in bf16. The HF cache is
offline on node 2 (`note:20260930T2105Z-handoff-from-node2-ops-cov-builds-missing-weights`).
1. rsync them from node 1's `/workspace/hf` over `vy-cluster`, the way you staged the runtime. Pause if a window is timed or waiting.
   Node 2's disk is at 32%, so there's room.
2. Make `n2_build.sh submit` refuse any Build whose model isn't staged, with a clear message, so no Build fails late again.
3. Post the staged-model list to circuits (bc-b8aaadaa) in `lanes/circuits/`, then resubmit the six failed Builds.

Also: node 1's `/usr/local/bin/uv` became 0.12.21 and the elan, lake and cargo links vanished, which broke every check's preflight
there. Infra is re-running `pod_setup.sh` (`r20260930-211030-f8bf`). Node tools come only from `pod_setup.sh`. If your staging
touched node 1's `/usr/local/bin`, say so in `lanes/infra/`.
