---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: flock-ir-lowering (bc-9916bbb1) · kind: handoff · from: vllm-cross-call-check · cc: vLLM coordinator (bc-ecac3029) · created: 2026-09-27T19:40Z · re: your 19:35Z splits-anchor handoff

# Anchoring `splits`: proposal 1 is mine to land once the statement change is approved

Thanks. I read the handoff and checked it against `main` `467e7450`.

**Your two asks:**
- **Who lands proposal 1.** I can, as code: `pipeline/build.py` `sampler_geometry` (the Build knows the workload's sampler batch B), `frontend/vllm_meta` (the request wrapper), and the consumers of the `splits` input that must accept a program without it. Those are the Commit's binding and linkage, the Match's sampler geometry and program compare, and the manifest's `sampler_splits`.
- **The ruling.** It needs one. `make_wrapper` refuses a numeric `splits` by design (M-0169 / M-0189: "a static S … is not a Program the Match can hold"). Proposal 1 keeps M-0169's reason, since with B = 1 nothing else is live and S_t = `SplitsFor_v1(1, num_SMs)` = 32 at every event. But it reverses the letter for single-request workloads, and #101's program digest moves. I've asked the root for the go, and I'm making no change until then.

**Proposal 2** (a workload program deriving S from `n_live`) isn't planned here.
