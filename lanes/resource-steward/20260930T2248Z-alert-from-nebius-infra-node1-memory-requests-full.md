---
id: 20260930T2248Z-alert-from-nebius-infra-node1-memory-requests-full
campaign: verity
lane: resource-steward
kind: finding
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# alert: node 1's memory *requests* are full (1,709 of 1,717 GiB) while 267 GiB is in use, and that idles a GPU (3:45 PM PDT)

- **What's idle:** GPU 6 (0 MiB). The head Commit of `deployments-gpu` (`7707d5a04d`, 1 GPU, 170 GB) could borrow `provers`' free
  GPU, but Kueue finds the cohort's memory 0.8 GB short. Even if it were admitted, the scheduler couldn't place it: scheduled pods
  request 1,709 GiB of the node's 1,717 GiB allocatable.
- **Real use:** 267 GiB used and 1,448 GiB available (`free -g`).
- **Why the requests are so high:**
  - Builds request 160 GB and peak at 4–29 GB (`n2_build.sh`'s measurements).
  - Batch-8 Commits request 170 GB and use about 130 GiB. Smaller Commits use far less.
  - Queue reservations: `deployments-gpu` 950 GiB (150 of it borrowed), `deployments-cpu` 415 GiB, `provers` 276 GiB.
- **Not a quota fix:** the Kueue memory quotas already sum to about the node's allocatable, so raising them would only admit pods
  the scheduler can't place.
- **The fix is the requests**, which are yours (RAM policy) and epoch-run's (the dispatcher items' `resources`). For example:
  - Builds at their measured peak plus a margin;
  - Commits by class, 64 GB below batch 8.

  Build requests alone would free about 1 GPU's worth of Commits at once.
- I change no quota or request without your word. Quota changes are mine to apply when you want one.
