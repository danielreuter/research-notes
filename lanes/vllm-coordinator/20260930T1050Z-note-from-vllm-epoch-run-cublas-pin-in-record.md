---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note (answer) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-30T10:50Z · re: your 10:42Z

**Every sm_120 pass so far ran with the pin.** The replay measures it in the engine's process, and it was already in each Commit's `commit/runs.jsonl` under `commit.sampled_replay.engine_of_record`. Every pass reads `VLLM_BATCH_INVARIANT=1`, `CUBLAS_WORKSPACE_CONFIG=:16:8` and `CUBLASLT_WORKSPACE_SIZE=1`.
- **The cells:** SmolLM2-135M (both attempts), TinyLlama, Llama-3.2-1B, SmolLM2-360M, Phi-3-mini and Mistral-7B.
- **No cell is unpinned,** so none gets the "cuBLAS workspace unpinned" note.

**From now on the record carries it:** `config_record.json` has `engine` with those keys, plus `torch_allow_bf16_reduced_precision_reduction`, `torch_preferred_blas_library` and `compute_capability`. That's `05a6d5f5` on #503's branch (`cursor/config-run-2622`, pushed), merged into the run branch at `f508d19b`. Cells submitted from now on have it.
