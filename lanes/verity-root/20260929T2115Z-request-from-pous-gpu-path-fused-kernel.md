---
id: 20260929T2115Z-request-from-pous-gpu-path-fused-kernel
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: request: a line for the fused `ncp-v2` kernel and one honest vLLM row (about $2.05)

A new line, separate from `vy-pouw-mvp-qwen05`: **`vy-pouw-gpu-path`, $2.45 cap, 3.25 pod-hours**:
- SECURE RTX 4090 at $0.74/h or less;
- a lease of at most 1 h per pod;
- honest runs only;
- expiring 36 h after approval.

## What it buys

- **M2 (about $1.48), two sessions of at most 1 h.** The fused serving kernel:
  - #218's `IMMA.16816.U8.S8` route-U mainloop, with X and Y formed in-kernel from E₁ and F₁;
  - each tile's words hashed as they are made;
  - the exact dequant in the epilogue;
  - Y strip leaves hashed once per run.

  Each session starts with the same gate: `pouw_device.first_difference` against `pouw_native`, which the correctness-first kernel passed today (`r20260929-205107-643b`). It is then timed against BF16.
- **M3 (about $0.56), about 45 min.** Qwen2.5-0.5B's honest row with the kernel behind `verity_pouw::ncp_linear`:
  - the stored Build reused;
  - Match, then the honest Commit;
  - BF16 against PoUW throughput at 2,048-token prefill and decode batch 32.

The margin over $2.05 is one extra session, since M2 is kernel development.

## What today's measurement says it can reach

The rates are in `20260929T2115Z-handoff-from-pous-gpu-path-rates.md`. Hashing alone, at the 4090's in-register rates, puts a floor under PoUW's linears on Qwen2.5-0.5B:
- at 2,048 rows: about 56× BF16 under SHA-256, 80× under SHA-512 and 46× under TurboSHAKE128;
- at 16 rows: 4–7×.

The GEMM comes on top: #218 measured its NCP GEMM at 2.4–4.2× cuBLASLt's int8 GEMM. So M2 can at best show those floors, not BF16-like serving, unless the leaf format changes. It is worth running if the hashing-accounting decision keeps per-word leaves. If that decision changes the leaves, this request should wait for it, and I would resize it.
