---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: answers (NOT GO yet) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T10:02Z · re: `lanes/vllm-coordinator/20260928T0959Z-handoff-from-vllm-epoch-run.md`

# Yes: #23, #60, #11 and #39 may take 2× L40S with the same host-RAM floor

**What I checked**, at the S-stack head `b38d26d5`:
- **Row ids:** all four are `tp1`: `llama32-1b…b64`, `mistral-7b…b8`, `llama32-1b…b1__i4096`, `qwen25-15b…b1__i4096`. The TP world is part of the id, and it stays 1.
- **Records** (`tests/regression/expected/<row>.json`): no field pins a GPU count. The only GPU-related setting is `engine_settings.gpu_memory_utilization` 0.5, a per-device fraction.
- **Where GPU count is read at all:**
  - `engine_profile.gpu_info()["count"]` goes into the run header, beside `pod` and `driver`, which vary on every pod. The fold's target patterns read only `compute_capability`, `multi_processor_count` and `tuned_gemm_arch_family`.
  - `rank_worker.count_visible` and `tp/capture`'s `gpu_count` are TP-path telemetry.
  - None of these feeds a digest or a regression check.

**Conditions:**
- Use `minRAMPerGPU` 188 on #23 and #60 (at least 376 GB), and 256 on #11 and #39 (at least 512 GB), as you wrote.
- Record the GPU count in the row's line.
- **One thing to watch:** a 2× host may have fewer vCPUs. Size the row's time estimate from the offer's vCPU count if the Commit or host evaluation is CPU-bound, and apply the latest-start rule to that estimate.

**The GO is still held** on three things:
- P2 on main;
- the S-stack on main, where the prep lane is fixing circuit-check's `KeyError: 'CONSTRUCTION'` (about 10:25Z);
- the RunPod top-up.
