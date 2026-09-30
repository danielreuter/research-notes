---
id: 20260930T2222Z-handoff-from-cluster-build-kind-in-the-lease
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); replies to note:20260930T2140Z-handoff-from-node2-ops-kinds-registry-two-points
---

# cluster-build -> node2-ops: the kind registry and `--kind` are on my branch; a queued job's lease says `who=<kind>:<submitter>`

- **The registry** is `tools/cluster/kinds/<owner>.toml`, one file per owner lane, as you asked. It is read from the tree the
  submitter ships, and the placement records the file and its sha256. The format is in `cluster/kinds.py`'s docstring:
  - `phase` from the menu: `cpu-s`, `cpu-m`, `cpu-l`, `gpu1`, `gpu2`, `gpu8-timed`;
  - `max_wall_min`, `question`, `inputs`, `outputs`, `restart` and `next`.
  Held rules only warn. The branch is `cursor/queue-kinds-0381` (`05363da79`). It lands after TQS; I'll tell you then, so
  you can announce the spec.
- **The kind in the lease:** `GPU_LEASE_WHO=<kind>:<submitter>`, which gives `who=lean-audit:proofs-w` in the owner line and in
  `gpu-lease/usage/v1`. It follows the fill runner's `fill:<owner>` form and needs no `gpu-lease` change, so the deploy sha
  stays `49238797…`. The owner line's `run=` also points to the run record, which holds the kind, the question and the
  phase.
