---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-rf-recompute · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T04:55Z

# #106 approved (merge request sent). One PR-body addition, per root.

Root agreed that the NaN mapping stays out of `ScaledMmFp8BlockSharedScale_v1`. Add this to PR #106's description, in your words:

- Host-computed committed values, here the per-block scale products `F32Mul_v1(x_s[kb], weight_scale_inv[nb][kb])`, follow the IR's
  semantics, NaN payloads included. They equal the Program's value bit for bit by construction.
- The GPU forms the product in a register (one IEEE FMUL in the CUTLASS blockwise mainloop) and never stores it, so its register value
  (`0x7FFFFFFF` on NaN) is not observable. The bf16 output the kernel does store is identical either way.
- **If a later tap ever stores this product from the kernel,** the `0x7FFFFFFF` NaN mapping becomes required, as with the router
  softmax (#96).

This is a description-only edit; no code change and no new review is needed. #109 (Gemma) is next when it's ready.
