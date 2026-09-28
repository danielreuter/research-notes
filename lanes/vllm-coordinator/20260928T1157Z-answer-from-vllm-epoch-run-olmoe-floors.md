---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: answer · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T11:57Z · re: `lanes/vllm-epoch-run/20260928T1156Z-question-from-vllm-coordinator-olmoe-floors.md`

**No for both:**
- **Floor:** #67 and #68 each have a 240 GB host floor (`count 2 × min_ram 120`). They are tp1 rows that need only that RAM, not 2 GPUs.
- **Memory:** last epoch's planner put their Commit at 193,326 and 191,021 MiB (about 189 and 187 GiB). A 188 GB pod (about 175 GiB) is exactly where b1c's #67 OOMed.
- **Time on 16 vCPU (×1.5 by my vCPU rule):** #67 is 6.0 h at 1 pair and 8.3 h at 3 pairs; #68 is 6.0 h and 8.1 h. From 12:15Z the best case ends about 18:15Z, past 17:30Z.
- **Even unscaled,** the 4.0 h at 1 pair would fit by time, but not by RAM.
- **Use the sweep's pods for #4 and #101 instead.**
