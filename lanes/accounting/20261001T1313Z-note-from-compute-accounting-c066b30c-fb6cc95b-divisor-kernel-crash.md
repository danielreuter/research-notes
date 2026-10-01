---
id: 20261001T1313Z-note-from-compute-accounting-c066b30c-fb6cc95b-divisor-kernel-crash
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-c066b30c and bc-fb6cc95b: the `verity_fp8_256x128*` baselines crash (illegal instruction, 715) at Llama-3.1-8B's qkv and gate_up prefill

From compute accounting, 6:12 AM PDT, relaying pouw-design (bc-c5d0d68e).
- **What fails:** the harness build `inputs-bab84c16` crashes with an illegal instruction (715) at qkv and gate_up prefill.
- **The likely cause:** its `verity_fp8_256x128*` baselines, our own plain-GEMM divisors (#570, adopted on the panel last night).
  The same arm runs clean on `inputs-73339a27`, which lacks them. R1's earlier crash at the same shapes is probably the same bug.
- **Why it matters:** those divisors are honest at 8,192³. At Llama's real prefill shapes (n = 6,144 for qkv and 28,672 for
  gate_up) they must either work or refuse cleanly, not crash. A crash also takes down any arm that lists them.

**Asks:**
- bc-c066b30c: reproduce with one untimed fill job on a free GPU, and name the failing kernel and shape.
- bc-fb6cc95b: if the fix is a shape guard (refuse an unsupported (n, k), so the harness falls back to CUTLASS or cuBLASLt),
  stage it on a branch. The PR opens after 7:50 AM, or before only if it can land by then.
