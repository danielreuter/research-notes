---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T09:59Z · re: `lanes/vllm-epoch-run/20260928T0913Z-answers-from-vllm-coordinator-community-sm89.md`

# Community sm_89 is wired in. One reading to confirm: the 4x rows may take 2x L40S with the same host-RAM floor

**Your 09:13Z conditions, now in the launcher and the pods:**
- **Offer order:** secure first, then L40 secure, L40S community, L40 community. Each is on-demand and at or below the row's secure rate. The H100 rows stay secure.
- **Checked at create:** the host must run CUDA 12.9 or later and meet the row's RAM floor, or the pod is terminated and the next offer tried.
- **Fail-fast:** `nvidia-smi`, torch CUDA init and `import vllm` must pass within 15 minutes of the pod's start. Otherwise the pod stops its bootstrap and the VM watcher terminates it.
- **Each row's line** records the cloud, the driver and any refused offers.

**The reading to confirm (veto if wrong):** #23, #60 and #11 (and #39 in wave 2) are single-GPU rows that use 4 GPUs only for host RAM. If no 4x L40S exists, the launcher tries 2x L40S with the same floor, at a lower rate:
- `minRAMPerGPU` 188 on #23 and #60 (at least 376 GB, against the floor of more than 251 GB);
- 256 on #11 and #39 (at least 512 GB).

**Stock at 09:58Z:** there's no 4x L40S or L40 on either cloud. 2x L40S comes and goes: community showed $1.58/h (Low) at 09:57Z, then none at 09:59Z. There's 1x L40S secure, and 2x L40 secure appeared at 09:59Z.
