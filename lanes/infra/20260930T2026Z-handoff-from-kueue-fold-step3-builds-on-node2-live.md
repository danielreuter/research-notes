---
id: 20260930T2026Z-handoff-from-kueue-fold-step3-builds-on-node2-live
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---

kueue-fold, step 3 has landed: a vLLM Build ran on node 2 as a Verity guest (48–95, scope-frozen in windows), reproduced node 1's program digests, and was preserved in R2. Its Commit is queued on node 1 through the dispatcher. vllm-coordinator has the one-line submit (`note:20260930T2025Z-handoff-from-kueue-fold-builds-on-node2-how-to-submit`); the Commit's pass follows there.
