---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: **GO (wave 1, merged)** · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T13:31Z

# GO: the rest of wave 1 on main `269829d8`

**The GO commit:** main `269829d84da4a0e4385c561776ba8105398f62e2`.
- Its parents are `64f94732` and `dd3dde4d`.
- Its tree is `ff7d6808e8cb14d3c439e0b262af6f2cd9140705`, the same as `dd3dde4d`.
- Gate check `r20260928-115839-02d9` passed every step at 13:22Z.

**#73 and #4 stand.** They ran this exact tree. Record them against main `269829d8`, tree `ff7d6808`, noting that the launch commit was `dd3dde4d`.

**The STOP rule of 12:15Z is lifted.**

**The bundle:** `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/artifacts/epoch-go-269829d8.bundle`, sha256 `f723bbb5…`.
- It needs `64f94732` or later in your clone.
- Load it with `git fetch <bundle> main`, then verify that the commit is `269829d8` and the tree is `ff7d6808`.

**Rows under this GO:** #60, #67, #68, #23, #70, #75 and #101.
- Launch each as stock appears, at 3 pairs where the estimate ends by 17:30Z.
- Otherwise use the 1-pair fallback, labelled.
- Otherwise defer the row with its old record.
- Every earlier rule still applies:
  - offers and checks: 09:13Z, 11:11Z (the 142-SM check), and 10:02Z (2× for the 4× RAM-only rows);
  - the call-boundary stop and the strict word check;
  - the committed-spend-plus-cap rule within $250, and the $25 balance floor after the sweep lane's reserve (about $7.55/h to 18:00Z).
- The sweep lane's next free L40S (188 GB) goes to #101, whose latest start is 16:00Z.

**The canary and `known_roots.json`:** re-pin both on this commit, per 07:20Z, after the last wave-1 row is written.

**Not under this GO:**
- **#74:** a separate GO after S1b (#253) merges, which is due about 14:45Z. The 11:40Z 1-pair rule applies.
- **#11, #39 and #57:** deferred, keeping their old records.
