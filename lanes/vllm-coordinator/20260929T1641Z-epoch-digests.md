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
| #67 | 14f027c3 | - | - | - | - | -, word check fast PASS, deferred: verdict None on a GREEN row (the class states PASS) | manifest-verify not ok | no recorded results under /workspace/fu-evidence/67/evidence/record/olmoe-1b-7b__ | r20260929-132621-8676 (?, ?x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 12.63 |
| #4 | 14f027c3 | - | - | - | - | -, word check fast PASS, deferred: verdict PASS on a FAIL row (the class states FAIL) | coverage: boolean facts changed ['recorded'] | verdict FAILED: $.pass: expected false != actual true | r20260929-144729-2e93 (?, ?x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 5.45 |
| #60 | 14f027c3 | e18d83144ec7174f / 9 req (b6a52c3ba2594404, ...) / 99823f09fc8cc446 | 9eebca050bec93b9 | 21df1c84e02ed68b | 17247d5bc00f280c (+7) | PASS, word check fast PASS, written (record stage re-run on the pod as r20260929-195918-d34b) 1abe1395 | r20260929-131812-29d4 (?, ?x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 14.64 |
