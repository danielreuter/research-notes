---
id: 20261001T0002Z-ask-from-nebius-infra-provers-gpu-borrow-while-capped
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# @infra: 5 of node 1's GPUs are empty while a `provers` job waits for one. Let `provers` borrow GPUs while the bundle cap paces Commits? (5:02 PM PDT)

- **Now:** `deployments-gpu` has 3 Commits admitted. The pacer releases none, because the projected bundles are 171 GB against the
  150 GB cap until `phi3b8g`'s replay deletes its 100 GB. So 5 GPUs hold no memory.
- **Waiting:** `pod-tcdefs-mxf4-edges2-347` (1 GPU, 8 vCPU, 24 GB) waits in `provers`. Its 3 GPUs are all used by proofs' jobs, and
  `provers` has `borrowingLimit: 0` on GPUs (Daniel's ruling, 7:34 AM PDT).
- **Option:** set `provers`' GPU `borrowingLimit` to 2 while the cap holds. `deployments-gpu` reclaims borrowed GPUs when its
  Commits are released, so a borrowing `provers` job could be preempted. Benches are safe only if they stay inside `provers`'
  own 3 GPUs.
- **This changes Daniel's ruling,** so it's yours or his to make. I apply it in a minute on a yes. Revert by setting the limit back
  to `"0"`.
