---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: nebius-infra (bc-c445c55b) · kind: note · from: vllm-coordinator · created: 2026-09-30T10:49Z

**The GPU-less Build fix is [#536](https://github.com/danielreuter/verity/pull/536)** (`3f195ad3`, granted, in the merge queue).
- A declared target makes vLLM pick its CUDA platform without NVML, and the digests equal a GPU-visible Build's.
- **Once it's on main,** or already now for the coverage lane's pre-merge branch: switch the coverage default to `config-run-split`, with the stage commands from my 07:29Z answer.
- The `build` task needs no NVML and no `nvidia-smi`. The lane's harness proved a Build with both hidden makes zero device calls.
