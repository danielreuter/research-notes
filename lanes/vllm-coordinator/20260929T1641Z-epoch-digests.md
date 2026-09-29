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
| #101 | 14f027c3 | 11e8da5d74b2c699 / 1 req (ec29fe03bd242277) / 66df03fba5674316 | 1ea8e220c8e4c98f | dfde1f7202483127 | 2b159fadcef19486 | PASS, word check fast PASS, deferred: no recorded results under /workspace/fu-evidence/101/evidence/record/llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager | r20260929-144629-282e (?, ?x NVIDIA L40S, 142 SMs, ? vCPU, driver ?) | 2.07 |
