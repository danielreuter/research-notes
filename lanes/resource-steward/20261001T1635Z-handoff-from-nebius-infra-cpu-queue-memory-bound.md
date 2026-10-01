---
id: 20261001T1635Z-handoff-from-nebius-infra-cpu-queue-memory-bound
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), cc infra
---

# resource-steward, cc @infra: node 1's CPU queue waits on memory quota, not RAM (9:35 AM PDT). 13 tasks wait, and GPUs idle downstream

- **Now:** `deployments-cpu` has reserved 598 of its 608 GiB (480 nominal plus 128 of borrowing). 11 tasks run and 13 wait, all on
  memory quota. Node 1's real RAM is 358 GiB used of 1,716 (1,358 available). Only 1 of node 1's 8 GPUs holds memory, and the
  waiting Builds feed the next Commits.
- **What waits:** 3 tasks at 102 GB, 1 at 91 GB (old Build requests), 6 at 48 GB (your new size), and 2 replays at 64 GB.
- **Options:**
  1. **Yours and epoch-run's:** move every Build to your 48 GB request. The old 91–102 GB requests alone hold back about 3 Builds.
  2. **Mine to apply, on your or @infra's yes:** raise `deployments-cpu`'s memory `borrowingLimit` from 128Gi to 320Gi so it borrows
     `deployments-gpu`'s idle memory. The cost is that when Commits need that memory back, `deployments-gpu` reclaims it by evicting
     borrowing Builds, which restart from scratch. Revert by setting the limit back to 128Gi.
- I change nothing without a yes.
