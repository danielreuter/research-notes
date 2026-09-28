---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: **GO (re-plan against the 23:30Z window)** · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T15:59Z · root decision 15:58Z

# GO: #101 now; then #74; then #60, #67, #68, #70 and #75 as stock and money allow

**The window:** the `vyv-` guard runs to 23:30Z. Every job timeout and per-row pod guard ends by 23:20Z, and each row starts only if its estimate ends by then.

## 1. #101: GO now, early start on main plus #297

**The GO commit:** `edac1cf6f65b84e7da209bf19dd93cfe65de6663`, with tree `9e41acb15cef29b4bf416cb7b43bacf11c7039d0`.
- This is my local merge of #297 (`81fd1414`, head of PR #297) onto main `432edb3b`. It merged cleanly, and its only diff from main is #297's two files.
- #297's own branch is based on an older main. When `research merge` lands #297, the landed tree should equal `9e41acb1`.

**The bundle:** `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/artifacts/epoch-101-297-edac1cf6.bundle`.
- sha256 `52a8739a742845e71a2acbcdd37e39f7583ce39603fd508f3c8ec21c2ce77bda`, ref `refs/tmp/epoch-101-297`.
- It needs `be354ab0` (train H) and `269829d8`, which your clone already has.
- Verify the commit and tree before starting.

**The row:** 1× L40S, L40 or RTX 6000 Ada (142 SMs), at least 94 GB, 1 pair (its record), `--word-max-gates GumbelTopPTokenSelect_v2=110000000`, cap $5.

**Recording:**
- Carry the commit `edac1cf6` and the tree `9e41acb1`, and hold the `expected/` write.
- I'll write the verdict after #297 lands. The record is written only if the landed main's tree equals `9e41acb1`.
- If the landed tree differs, it's written only if the diff provably doesn't touch #101's Build. If neither holds, the record is discarded.

## 2. #74: GO when a 2× H100 secure is in stock

- **On:** main `432edb3b`, which carries S1b. Use the H bundle plus main, or the #101 bundle's parent `432edb3b`.
- **The row:** 1 pair, labelled `n_runs` 6 → 2, run eager, cap $49.
- **Latest start:** about 17:40Z, for 5.4 h plus the S1b overhead ending by 23:20Z. After that, #74 stays deferred.

## 3. Then #60, #67, #68, #70 and #75

- **On:** main `432edb3b`, in latest-start order, when their shape appears. Use 3 pairs if the estimate ends by 23:20Z, else 1 pair (labelled), else defer.
- **Caps:** #60 $24, #67 $13, #68 $13, #70 $6.5, #75 $12.
- These rows are held back by money more than by stock (see below). **Launch only if the rule below passes at that moment.**

## The launch rule, before every launch

- **The balance test:** (RunPod balance) − (the remaining caps of every running row) − (the sweep lane's $7.55/h to 23:30Z) − (POUS $15) − $25 must be at least the new row's cap. Otherwise don't launch, and write me one line.
- **The epoch test:** the committed-spend-plus-cap rule within $250 also applies.

**#11, #39 and #57 stay deferred.**
