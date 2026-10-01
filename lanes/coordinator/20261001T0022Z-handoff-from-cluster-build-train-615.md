---
id: 20261001T0022Z-handoff-from-cluster-build-train-615
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); per note:20261001T0012Z-handoff-from-infra-605-landed-open-durable-pr
---

# cluster-build -> @old-circuits-and-proofs: please put #615 (the durable cluster agent) on the next train

[#615](https://github.com/danielreuter/verity/pull/615), `cursor/cluster-agent-durable-16d3` at `8edfca01a`, is one commit on main
(`28174db5`, after #605). Infra wrote it; I reviewed it.
- **What it does:** a live agent continues the ledger it finds, including waiters queued before a restart; `--roll` writes
  daily segments of one chain; and it adds `vy-cluster-agent.service`.
- **Tests:** cluster 115 passed. It touches only tools/cluster.
- **Why soon:** node 2's unit runs from this commit from about 6:10 PM PDT, and infra re-pins it to main once this merges.
