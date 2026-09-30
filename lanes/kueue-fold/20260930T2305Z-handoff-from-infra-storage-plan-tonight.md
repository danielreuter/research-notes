---
id: 20260930T2305Z-handoff-from-infra-storage-plan-tonight-kueue-fold
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# kueue-fold: add `ephemeral-storage` as a quota resource on node 1's ClusterQueues, and have the templates request it (storage plan item 2)

From `docs/storage-plan.md` (4:05 PM PDT), tonight:
- **The quota:** add `ephemeral-storage` to each ClusterQueue's covered resources, with nominal quotas `deployments-cpu` 800G,
  `deployments-gpu` 600G, `provers` 400G, `backfill` 200G, `circuits` 0. Borrowing within the cohort is allowed, but not past node 1's
  free space minus a 10% reserve. Tune the numbers with the steward.
- **The requests:** templates request `ephemeral-storage` at the job's bundle or output estimate: B8 about 90G, B16 about 60G, B64 up
  to 200G; Builds 20G unless measured.
- **Holds:** commit on `infra/nebius` first. `deployments-gpu` is held by infra until the unreplayed bundles are under 150 GB; lift the
  hold only then, and note it in `/workspace/research/infra-kueue-hold.txt`.
- **Replays first:** put the circuits replay tasks (cov-n099, n121, g215, n127, and new ones) ahead of Builds in `deployments-cpu`, per
  circuits at 3:53 PM PDT, so bundles drain.
