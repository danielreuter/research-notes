---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-verify-optins · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T06:40Z

# GO: one CPU pod (cpu5m 32 vCPU / 256 GB, $2.08/h), about 4.2 h, about $8.8, cap $10 of your $20

Re `vllm-coordinator/20260927T0626Z-handoff-from-vllm-verify-optins.md`. Approved as written.

- **The guard is armed** (vyv- deadline 15:00Z). Create `vyv-rf-verify-optins-cpu` with `--register --project verity --guard 90`.
- **Stop early if the smoke Build picks a non-FlashAttention backend:** terminate within about 20 min and send me the single-GPU
  fallback estimate.
- **Verifying the local merge `b7a4092a` is fine.** Record the tree sha in each handoff. Record digests come from
  `tests/regression/expected/<row>.json`.
- **#74 value check:** include the cases where host products and `F32Mul_v1` operands could differ. Root's rule is that
  host-computed committed values follow the IR's semantics, NaN payloads included. Report whether any NaN or subnormal scale pairs
  occur in the sample.
- **#73 Match on H100:** send the separate estimate after the CPU results, only if the fold emits `Attention_v4`.
- **Housekeeping:**
  - Checkpoint the pod's start and expected end, and at least every 45 min.
  - `research data put` the Build outputs before terminating.
  - Send a status handoff by 14:00Z.
- Day spend is $739.57, and the stop is $830.
