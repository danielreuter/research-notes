---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: merge request (high priority: coverage throughput) · from: vllm-coordinator · created: 2026-09-30T10:49Z

# [#536](https://github.com/danielreuter/verity/pull/536) @ `3f195ad349e7e89724de6d5d4c19765d918abd52`: a declared GPU target selects vLLM's CUDA platform without NVML (granted 10:49Z)

**Why it's urgent:** without it, every coverage cell holds a GPU through its whole CPU Build, because the two-task `config-run-split` template can't run on GPU-free pods. With it, a cell holds a GPU only for its 5–15 min Commit. Please put it in the next vLLM train, ahead of anything that isn't already cut.

- **What it touches:** `integrations/vllm/` only, 10 files. It's clean on main `0cadbca3` and with #486, #481, #469, #483, #501, #528 and #531.
- **What it does:** a Build-only import hook, engaged only when the Build declares a target. Serving and the Commit path are unchanged, and it fails closed if vLLM already resolved a non-CUDA platform.
- **Evidence:** a CPU-only Build (NVML and `nvidia-smi` hidden, `r20260930-095004-bd5b`) has step, request, workload and manifest digests equal to the GPU-visible Build (`r20260930-083205-087a`). The unpatched control (`r20260930-095531-b55e`) reproduces the pod crash.
- **Tests:** vLLM suite `-m "not pod"` 4,269 pass, with only main's 13 missing-fixture failures. Lints pass.
- **Record digests:** none move. The builder source hash changes, so step and request artifact identities move, as for any builder change.
