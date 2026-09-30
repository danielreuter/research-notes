---
id: 20260930T2228Z-handoff-from-infra-delivered-output-metric
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: add the delivered-output fields to node 2's `infra-pool.json`, the same as kueue-fold's for node 1

- **The fields:** `leased_gpu_s`, `delivered_gpu_s` and `delivered_share` per hour. Leased time comes from `lease-usage.jsonl`'s `held_s`.
  Delivered means the fill job exited 0 with its declared outputs present, or the run's Attempt verdict passed. Filler is never
  delivered.
- **The spec:** `lanes/infra/20260930T2220Z-draft-node1-mps-commit-packing-cutover.md`, second half. Daniel approved it at 3:22 PM PDT.
- **Timing:** agree on the names with kueue-fold, then ship before 6 PM PDT, since T2 is reported on these fields.
