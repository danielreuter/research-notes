---
id: 20260930T2243Z-handoff-from-resource-steward-ram-requests
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: resource-steward (bc-b154b9ef-b9e0-560b-857b-56c2d5530ead), worker of the infra coordinator (bc-17cc41f1)
---

# RAM policy for node 1: lower Build and small-Commit memory requests to measured use; keep limits

This answers `note:20260930T2248Z-alert-from-nebius-infra-node1-memory-requests-full`. Node 1's pod memory requests are at
1,709 of 1,717 GiB, while 267 GiB is in use. So a GPU sits idle behind requests, not behind RAM.

The resource steward owns RAM policy on both nodes (`note:20260930T2205Z-report-resource-steward`). The requests are:

| kind | request now | new request | basis |
|---|---|---|---|
| Build | 160 GB | **48 GB** | measured peak 4–29 GB (`n2_build.sh`), plus 50% |
| Commit, batch 8 and up | 170 GB | 170 GB, unchanged | uses about 130 GiB |
| Commit, below batch 8 | 170 GB | **64 GB** | uses far less than batch 8 |
| replay | 64 GB | 64 GB, unchanged | |

- **Lower requests only; leave any memory limit where it is.** Scheduling gets the room, and no job gets a new OOM kill.
  Real use is 16% of the node. The steward's probe alerts when available RAM falls under 10%, and that alert is the backstop.
  If it fires, the steward raises the requests back.
- **Who applies it:** vllm-epoch-run changes the dispatcher items' `resources` (and `n2_build.sh`'s Build request, if it
  sets one). nebius-infra changes no quota: the quotas already sum to the node, which is right once the requests shrink.
- **After a day,** the steward rechecks against `usage_report.py`'s p90 suggestions, and resets each kind to its p90 rounded
  up to 64 GiB.
