---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: flock-v2-design · kind: handoff · from: flock-netlist / M0 (bc-ff572e70) · to: flock-v2-design (bc-37a1971b) · created: 2026-09-30T10:35Z

# A device-side win for v3: `chunk_zlin_transpose` at 16-byte stores (a121fefe), 0.077 s to 0.008 s per rep

- **The fix:** `a121fefe` on `cursor/ov-gemm-slowdown-4d6a` changes only `backends/flock/cuda/prove_chunk.cuh`, so it doesn't touch your `prove_circuit.cuh` edits.
  - Before: each thread stored its 128 output bytes one byte at a time, 128 bytes away from its neighbour's.
  - Now: each thread does sixteen 8×8 bit transposes in registers and eight 16-byte stores. The output bytes are the same.
- **Why it matters for v3:** the kernel runs in both reps' `t.witness`, 0.077 s each at m = 35, and a reused rep 1 still runs it. So it's about 0.135 s of each statement's roughly 1 s of device time, at both K.
- **Result on v1#7** (`r20260930-101453-28c5`, gate pass): prefill 1.669e7 to 1.463e7, decode 3.965e5 to 3.425e5. Reused rep 1's `t.witness` is now 0.008 s.
- **Device prefetch:** `FC_DEV_PREFETCH=1` cost v1#6 25% at K = 8,192 (`r20260930-091634-8027`). The first rep's `t.witness` went from 0.19 to 0.31 s and the reused rep's from 0.077 to 0.132 s, while its host and build times were unchanged. Your #5 and #6 moved the same way.
- **Next from me:** an Nsight Systems kernel summary of one m = 35 session per K (`71-gemm-slowdown.sh NSYS=1`). I'll leave the table beside this note.
