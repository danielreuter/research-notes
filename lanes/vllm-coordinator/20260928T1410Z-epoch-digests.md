---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: report · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T14:10Z · re: `lane-briefs/vllm-epoch-run.md` "Out"

# Re-baseline epoch: per-row digests (Q_word v1 as the partition of record)

One line per row as it lands. Digests are the first 16 hex; the full values are in `20260928T1410Z-epoch-digests.json` beside this file. "written" means
`rebaseline write` took the row (`expected/` commit on the lane's branch); "deferred" means it was not written, with the reason.

| row | main sha | step / request / workload Program digests | manifest | run root | partition digest | verdict | run id | $ |
|---|---|---|---|---|---|---|---|---|
| #4 | 269829d8 (ran dd3dde4d, same tree) | 63c109fc625d6234 / 17 req (81d58d68b4d97371, ...) / 04f8516be70400c3 | 0cc516b3977253ad | a635c2f1c568b384 | 4b333410d2279c7a (+15) | PASS, word check rebuild PASS, deferred: Commit PASS on a FAIL-class row, for audit (coordinator 16:53Z): Build art:84ec56f4 (side-store art:876db263), records art:013671cf, large art:b604b4df, regress | r20260928-131016-78c9 (secure, 1x NVIDIA L40S, 142 SMs, 128 vCPU, driver 580.126.09) | 4.84 |
| #101 | fe7931d5 | 11e8da5d74b2c699 / 1 req (ec29fe03bd242277) / 66df03fba5674316 | 1ea8e220c8e4c98f | - | 2b159fadcef19486 | -, word check not reached, deferred: Match FAIL on a GREEN row (4th try, fe7931d5): the Program binds GumbelTopPTokenSelect_v1 x32 but the fold binds GumbelTopPTokenSelectSharedGreedy_v1 x32 (hist  | r20260928-175437-cfe5 (secure, 1x NVIDIA L40S, 142 SMs, 128 vCPU, driver 580.159.03) | 1.01 |
| #23 | 269829d8 | 85f492e1776ef102 / 65 req (adf3925e94ac0f5d, ...) / 53085015775ce097 | 004a5bdabb332d8d | - | 004b9870fe601b9c (+63) | NOT_RUN, word check fast PASS, deferred: NOT_RUN (admission): Commit refused by F-dA-15, 483 GiB predicted > 351 GiB pod; to the follow-up epoch on a >=512 GB host, old record kept (1 pair, time fallback: n_runs 6 -> 2) | r20260928-135923-53d9 (secure, 2x NVIDIA RTX 6000 Ada Generation, 142 SMs, 112 vCPU, driver 580.159.04) | 8.50 |
| #73 | 269829d8 (ran dd3dde4d, same tree) | a43b590ebf3c7538 / 9 req (73e6cf3e04a034ce, ...) / 357b965dca2497df | 466e67184d165a1c | 588c14eb147c336b | 055742b8c997fb20 (+7) | PASS, word check fast PASS, deferred: for the coordinator: harness coverage misses norm_scales (69020; the Commit's own coverage OK, 0 missing) + 2 GM fold pins moved; record kept (1 pair, time fallback: n_runs 6 -> 2) | r20260928-121849-ff8b (secure, 2x NVIDIA H100 80GB HBM3, 132 SMs, 208 vCPU, driver 580.126.09) | 55.05 |
