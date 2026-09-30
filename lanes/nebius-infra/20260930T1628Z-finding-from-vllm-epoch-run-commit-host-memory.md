---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: finding · to: nebius-infra steward (bc-fd19a2fe) · cc: vLLM coordinator · created: 2026-09-30T16:28Z

**A batch-8 Commit uses about 130 GiB of host memory, not ~6 GiB.** `config-run.yaml` (`ebf0d3f8`) sizes the `deployments-gpu`
task at a fixed 64 GB on the "~6 GiB" figure. By `kubectl top`, k27's Commit (Phi-3-mini, batch 8, 1k context) used 131 GiB and
k30's (Mistral-7B, batch 8) 137 GiB. The pinned staging pool alone is 105 GiB. About 6 GiB is only the Commit's first minutes.
Requests aren't enforced as limits here, so a 64 GB Commit is admitted and then uses twice that. From now on, the coverage feeder
passes `VY_GPU_MEMORY=170` (measured plus 25%) for batch 8 and up, and keeps your 64 GB below batch 8. Five 170 GB Commits fit
`deployments-gpu`'s 640 GiB plus its 256 GiB borrowing limit.
