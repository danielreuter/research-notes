---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T10:42Z

**The red team's `cublas-selection-stable` finding** (`r20260930-080344-10e2`, `-101118-5f25`): cuBLAS(Lt) picks a different kernel for 448 of 780 shapes when the workspace setting changes. With vLLM's workspace pin, the choice is identical across two dies.

**Check that every config record carries the pin's value.**
- Record the effective `CUBLAS_WORKSPACE_CONFIG` (or whatever the batch-invariant path sets) in the environment facts of `config_record.json`.
- If it already does, tell me the field. If not, add it to the record in your next run-branch change; it's a record field, not an engine change.
- A cell run without the pin gets `ov.note "cuBLAS workspace unpinned"`.
