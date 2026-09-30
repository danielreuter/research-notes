---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde; cc the backend GPU sweep lane bc-ea1c2c4f) · kind: handoff · from: vllm-coordinator · created: 2026-09-30T05:27Z

# The follow-up epoch is complete: 4 rows written, 8 deferred

- **GO:** 2026-09-29T13:04Z on main `14f027c3`, with Q_word v1 as the partition of record.
- **Rows written** on `cursor/followup-epoch-expected-2622`, all pushed, not merged; they reach main through the queue:

| row | expected commit | step / workload Program | manifest | run root | note |
|---|---|---|---|---|---|
| #101 | `dd8b6159` | `11e8da5d74b2c699` / `66df03fba5674316` | `1ea8e220c8e4c98f` | `dfde1f7202483127` | record art:90d543d8, rebuilt off-pod |
| #60 | `1abe1395` | `e18d83144ec7174f` / `99823f09fc8cc446` | `9eebca050bec93b9` | `21df1c84e02ed68b` | 9 requests |
| #4 | `45b9125c` | – | – | – | FAIL → GREEN (Daniel, 20:12Z); record art:7b437ce1; regenerator #439, which conflicts |
| #70 | `3485ad74` | `947b32e706e7fb92` / – | `4e4dcf8decfbc261` | – | FAIL reproduced; `program_digest` forced |

- **Full digests:** `lanes/vllm-coordinator/20260929T1641Z-epoch-digests.{md,json}`.
- **Deferred with their old records:** #39, #11, #67, #68, #75, #74, #57, #23. The reasons are in `lanes/vllm-coordinator/20260930T0500Z-report-from-vllm-epoch-run-followup-epoch-final.md`. The config sweep (`vyv-cov-`) supersedes re-running them.
- **Spend:** the lane counts $209.87. The guard's `vyv-rf-epoch-` line reads $215.23 at 05:25Z, with no epoch pods running; the difference is teardown and smoke-test tail. The line expires at 08:00Z. The RunPod balance is $134.
- **For bc-ea1c2c4f:** #101's written digests above replace the ones your sweep compared against, if you key on `expected/`.
