---
id: 20260930T2228Z-handoff-from-infra-delivered-output-metric-approved
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# kueue-fold: ship the delivered-output metric into the pool files. Daniel approved it (3:22 PM PDT), and node 1's targets are now measured on it

- **The spec:** the second half of `lanes/infra/20260930T2220Z-draft-node1-mps-commit-packing-cutover.md`.
- **Fields:** add `leased_gpu_s`, `delivered_gpu_s` and `delivered_share` per node and per hour, marked provisional until recomputed at +1 h,
  to `/workspace/usage/infra-pool-n1.json`.
- **Node 2:** node2-ops adds the same fields to `infra-pool.json`; agree on the field names with it in `lanes/node2-ops/`.
- **Priority:** before the node-1 executor. It feeds T2 tonight and T4.
- **Console:** tell it in `lanes/console/` once the fields exist. Busy % stays in the files beside them, as the secondary objective.
