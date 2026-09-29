---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: report · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-29T16:41Z · re: `lanes/vllm-epoch-run/20260929T1304Z-GO-from-vllm-coordinator-followup-epoch.md`

# Follow-up epoch: per-row digests (GO 2026-09-29T13:04Z on main 14f027c3, Q_word v1 as the partition of record)

One line per row as it lands. Digests are the first 16 hex; the full values are in `20260929T1641Z-epoch-digests.json` beside this file. "written" means
`rebaseline write` took the row (`expected/` commit on the lane's branch); "deferred" means it was not written, with the reason.

| row | main sha | step / request / workload Program digests | manifest | run root | partition digest | verdict | run id | $ |
|---|---|---|---|---|---|---|---|---|
| #101 | 14f027c3 | 11e8da5d74b2c699 / 1 req (ec29fe03bd242277) / 66df03fba5674316 | 1ea8e220c8e4c98f | dfde1f7202483127 | 2b159fadcef19486 | PASS, word check fast PASS, written (recovered off-pod; 2 checks sanctioned) dd8b6159; note:20260929T1743Z-answer-from-vllm-coordinator-101-gate; record art:90d543d8 | r20260929-144629-282e (secure, 1x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 2.07 |
| #60 | 14f027c3 | e18d83144ec7174f / 9 req (b6a52c3ba2594404, ...) / 99823f09fc8cc446 | 9eebca050bec93b9 | 21df1c84e02ed68b | 17247d5bc00f280c (+7) | PASS, word check fast PASS, written (record stage re-run on the pod as r20260929-195918-d34b) 1abe1395 | r20260929-131812-29d4 (?, ?x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 14.64 |
| #4 | 14f027c3 | - | - | - | - | -, word check fast PASS, written (reclassified FAIL → GREEN: Daniel, 2026-09-29T20:12Z, via root) 45b9125c; record run r20260929-194627-4b5f, record art:7b437ce1 | r20260929-144729-2e93 (secure, 1x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 5.45 |
| #39 | 14f027c3 | 6bda7a53400b532a / 1 req (-) / - | - | - | - | -, word check not reached, deferred: the Build stage's own 4 h cap (`min(14400, 900 × scale)`) was hit on the second half; a rerun needs > 8 h on 4× L40S (Build art:b9cb60d6 and records art:1b3ab37 | r20260929-160603-ab18 (secure, 4x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 18.75 |
| #70 | 14f027c3 | 947b32e706e7fb92 / 0 req (-) / - | 4e4dcf8decfbc261 | - | 28a0beb4a9087b8a (+15) | -, word check fast PASS, written (FAIL reproduced; program_digest forced) 3485ad74; record run r20260929-210427-1b02 | r20260929-164634-7d85 (secure, 2x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 9.44 |
| #11 | 14f027c3 | 920ee43e66872679 / 1 req (088e94fa71d3ba72) / d9593e27c279b254 | - | - | - | -, word check not reached, deferred: the job end (21:25Z) stopped the Build's manifest step (rc=-15) after the derives (rc=0/0, 8001 s) and the workload Program passed; Build art:b5c8b883 kept | r20260929-155228-da0d (secure, 4x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 24.30 |
| #75 | 14f027c3 | 4c1d169838bfe71f / 0 req (-) / - | 57194b91524710a7 | - | 0d50c62f98c34ace (+3) | -, word check fast FAIL, deferred: the resume from a stored Build failed (r20260929-214119-f482: word check found 0 Q_word lines in manifest.log); first job Build art:a0fd36e3, records art:85cc20 (1 pair, time fallback: n_runs 6 -> 2) | r20260929-160931-2778 (secure, 2x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 13.48 |
| #67 | 14f027c3 | - | - | - | - | -, word check fast PASS, deferred: the resume from a stored Build failed (on #68 and #75; not launched for #67); first job Build art:9adf9818, records art:671d7bb5 | r20260929-132621-8676 (secure, 2x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 12.63 |
| #68 | 14f027c3 | 00ffdfc33f2e2b35 / 33 req (bf37be0d2b3f7c2a, ...) / 4861c8b88f6e81dc | f3b7a0ff2cb9886e | - | 0c69c14f033f177d (+31) | NOT_RUN, word check fast PASS, deferred: the resume from a stored Build failed (r20260929-212049-6e37: Commit NOT_RUN, 0 runs); first job Build art:9b079a8c, records art:5dd4374d | r20260929-145326-613a (secure, 2x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 17.51 |
