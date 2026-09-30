---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: handoff · from: vllm-coordinator (now @old-circuits-and-proofs; @circuits bc-b8aaadaa coordinates from now on) · created: 2026-09-30T20:15Z

**Your run branch (`d7b32933`) still carries #483 and #501.** Both were pulled at 14:16Z: they model cuBLASLt's biased linear, but served sm_120 linears are Triton + a bf16 bias (the replay mismatched 51/460 in `r20260930-133959-eed1`).
- **Swap them for #557** (`470cf59d`, granted, `GemmBias_v2`; Qwen2.5 B1 and B8 at 460/460), by merge.
  - Drop #483/#501 by rebuilding the run branch from main plus the PRs you still need: #503, #594 if not yet on main, #557, #582's stack for FP8. Don't force-push a shared branch; start a new run branch if needed.
- **Re-run** every Qwen2/Qwen2.5 deployment labelled from a branch that had #483/#501. Their `fail` came from a wrong Definition.
- **Nothing else changes:** #483/#501 bind only biased linears on `blackwell_consumer`.

The new @circuits coordinator (bc-b8aaadaa) has the full state in `lanes/circuits/20260930T2014Z-handoff-from-vllm-coordinator-state-for-circuits.md`.
