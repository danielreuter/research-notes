---
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

20260930T1000Z vllm-config-run-tp2: the CPU-only Build for declared GPU targets is on branch `cursor/build-cuda-platform-3847`, head 3f195ad3 (off main). On vy-nebius-1 the SmolLM2-135M rtxpro6000 row, built with no GPU from the same tree 2847317c as the GPU-visible Build r20260930-083205-087a, gives equal step, request, workload and manifest digests in two runs: r20260930-095004-9211 (`CUDA_VISIBLE_DEVICES=` only) and r20260930-095004-bd5b (NVML and nvidia-smi also hidden). Negative control r20260930-095531-b55e: the unpatched tree with NVML hidden crashes the Build ("Device string must not be empty"). All runs are labelled and synced. The full `-m "not pod"` suite is running on the final head; the handoff follows.
