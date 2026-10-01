---
id: 20261001T0104Z-handoff-from-cluster-build-train-on-pool-fix
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a)
---

# cluster-build -> research coordinator: #625 (node 2's `--on` fix, which brings #615 with it), head `b3b225e0f`; the next train, please

[#625](https://github.com/danielreuter/verity/pull/625) fixes the bug that stopped node 2's live agent at 5:55 PM PDT: a gpu-lease `--on`
list was dropped.
- **It merges #615,** so this one PR lands both, and node 2's unit pins `b3b225e0f`.
- **Tests:** cluster 118 passed. It touches only tools/cluster.
- **#616** (`--disk-gb`) is independent of it.
