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
| #101 | 269829d8 | 83629e4eb35a2058 / 1 req (2df85d9c606116f7) / - | - | - | - | -, deferred: Build FAIL: the workload Program compose can't decode TopPKeepWord_v1{V=128256,S=32} (verity.ir.codec: alias to argument 0 of node 41 names an argument of an ea | r20260928-134402-b58d (secure, 1x NVIDIA L40S, 142 SMs, 256 vCPU, driver 580.173.02) | 0.49 |
