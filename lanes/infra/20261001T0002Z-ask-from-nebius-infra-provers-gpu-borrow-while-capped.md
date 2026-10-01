---
id: 20261001T0002Z-ask-from-nebius-infra-provers-gpu-borrow-while-capped
campaign: verity
lane: infra
kind: handoff
status: done
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

**Update, 5:05 PM PDT: applied.**
- Daniel's 7:34 AM PDT no-borrow ruling was superseded at 12:12 PM PDT ("one pool, one scheduler, borrowing both ways incl CPU,
  no ceremony"; the verity-top checkpoint), so no new ruling was needed.
- `provers` now borrows up to 5 idle GPUs, plus CPU 96 and memory 416Gi. The CPU and memory limits were already live from infra's
  4:45 PM PDT change and are now in the file.
- The Commits reclaim borrowed GPUs: `deployments-gpu` has `reclaimWithinCohort: LowerPriority`, and prover jobs run at 100–300,
  below the Commits' 600.
- `infra/nebius` `e8337c6b5`. The live objects equal the file (`kubectl diff` rc 0).
- A timed bench should stay inside `provers`' own 3 GPUs, since a borrowed one can be evicted.
- `pod-tcdefs-mxf4-edges2-347` is running.
