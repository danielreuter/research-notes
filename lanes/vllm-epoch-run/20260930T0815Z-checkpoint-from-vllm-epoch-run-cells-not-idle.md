---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-09-30T08:15Z

**No cell has been idling on the FA2 tap.** The 07:27Z four failed on tooling and were resubmitted: the old template had no `PY`, `device_id` ran `nvidia-smi` on the CPU build task (fixed in `b27ab8a0`), and the two-task build task has no vLLM platform (note to nebius-infra 08:10Z). Since 08:05Z, k01-k04 have run as one-GPU `config-run-row` jobs 77-80, all doing real work: k01 has been in its Build since 08:10; k02 finished its bootstrap at 08:12 (a per-job hidden_gpu load of 131 s); k03 and k04 are about 2 min behind the bootstrap lock. I could not fetch `infra/nebius` `73998c0e` (GitHub auth refused, and it is not in vy-nebius-1's repo), so nothing was moved to the two-task template. k05-k16 are being queued as PENDING jobs, which hold no GPU.
