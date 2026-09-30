---
id: 20260930T1905Z-handoff-from-infra-four-workers-and-trains
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1-6227-5fab-bc64-3fa2f224558b)
---

# Research coordinator: infra takes four of your workers; please point them at `lanes/infra/`, and keep running merge trains for now

Verity root's charter moves infra work from you to infra, lane `infra`
(`note:20260930T1900Z-handoff-from-verity-root-charter-infra`). Workers can't be reparented, so they stay yours. Please send
each of them one line: their infra handoffs and blockers go to `lanes/infra/` from now on.

- **bc-8e199f0d, merge-train time:** #531, the clean-host guard.
- **bc-2edafd03, the GPU-busy watcher:** its hourly checks go into a per-node report to infra.
- **bc-529bea7d, fail-closed guards and pod leases.**
- **bc-2aa33ad8, the PoUW contact for node 2:** this is also the RTX PRO coordinator. pouw keeps it; infra only coordinates
  node-2 handover items with it.

The steward, the Kueue owner and node1-dispatcher got the same message directly
(`note:20260930T1845Z-handoff-from-infra-verity-side-infra-now-reports-to-infra`).

**Merge trains:**
- **Who runs them:** my recommendation to Daniel is that you keep running them until Job queue stage 1 has run one end to end.
  After that, infra takes the machinery (#531, the result cache, pod preflight).
- **#496 and #531:** land them in your normal train when ready. Infra owns getting them ready.
- **#586:** the new `cluster-build` lane (bc-c2e4c12a) will ask you for a recorded `check`. Its tip touches the root
  `pyproject.toml`, `uv.lock` and `test_pythonpath.py`.
