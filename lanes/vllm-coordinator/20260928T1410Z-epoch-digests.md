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
| #101 | edac1cf6 | 11e8da5d74b2c699 / 1 req (ec29fe03bd242277) / 66df03fba5674316 | - | - | - | -, word check not reached, deferred: Build FAIL (3rd try, edac1cf6): the manifest step raises KeyError 'GumbelTopPTokenSelect_v2 is not a registered Definition' (query.program_view.definition_ports | r20260928-160311-303b (secure, 1x NVIDIA L40, 142 SMs, 256 vCPU, driver 580.178.04) | 0.43 |
