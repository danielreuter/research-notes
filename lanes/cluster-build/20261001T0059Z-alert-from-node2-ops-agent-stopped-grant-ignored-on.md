---
id: 20261001T0059Z-alert-from-node2-ops-agent-stopped-grant-ignored-on
campaign: verity
lane: cluster-build
kind: alert
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

# cluster-build: I stopped node 2's live agent at 5:55 PM PDT. It granted GPU 0 to a request pinned to `--on 2,3,4,5,6,7`, and the node sat 8/8 idle

The details and the fix list are in `note:20261001T0058Z-alert-from-node2-ops-agent-stopped-grant-ignored-on`, in `lanes/infra/`.
- **The grant:** `grant.355694` = `0`, for wait file `wait.1790815909578099857.355694` (`on=2,3,4,5,6,7`, run `r20261001-005132-35d9`).
- **The evidence:** the ledger is in `live/20260930T2320Z/`, with seq 527 the submit. `decisions.jsonl` was last written at 00:45:34Z.
- **The node now:** `live/STOP` is in place, and node 2 runs on today's rules.
- **Please:** start the agent again, or the unit, only with `on=` honored and a pinned-request test. Remove `STOP` when you do.
