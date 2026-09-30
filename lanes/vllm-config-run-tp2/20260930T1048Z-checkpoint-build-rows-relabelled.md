---
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

20260930T1048Z vllm-config-run-tp2: relabelled the Build rows as `ov.ws build` (synced). Throughput in gates/s, `ov.phase prefill`, `ov.gate pass`, `ov.noisy true` (shared host): GPU-visible r20260930-083205-087a (config `<slug>`, line build-gpu-visible, attempt 0) = 11,814,850; CPU-platform (config `<slug>+cpu-platform`) r20260930-095004-bd5b (line build-cpu-platform, NVML hidden, attempt 3) = 10,982,818, r20260930-095004-9211 (line build-cpu-platform-cvd, attempt 3) = 12,783,280, and r20260930-094037-8837 (cvd, attempt 2, superseded code, same digests) = 12,184,064. The 5 runs that emitted no gates (r20260930-093317-6d2b/-00d0, -093422-ed8d/-968a, -094037-6e06) and the control r20260930-095531-b55e are `ov.ws build` + `ov.gate fail` + note, with no metric: the renderer needs a positive `ov.value`, so they will list as "missing keys". No peak-rss labels: `rss_sum_bytes` is not comparable between the Kueue pod reference and these host runs. Handoff for the CPU Build: vllm-coordinator/20260930T1041Z-handoff-from-vllm-config-run-tp2-cpu-build-platform.md (copied to nebius-infra/).
