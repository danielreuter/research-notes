---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-24T23:22Z
---

# verified: RTX 5090 NVFP4 A-GKR art:ad8f92b9 (supersedes art:fe57e68b in the same cell; verdict art:37ed86f2)

This is lane agkr-nvf4's faster attempt (ab57df0a, fp4-nvf4, 0.314 s median; the earlier cell was 1.044 s). It is now
`verified=accepted --by verify-po` with `same_device=false`. Verdict art:37ed86f2 is PRESERVED.
- The verifier is the same one as in my 22:07Z handoff: `backends/gkr/verifier` at ab57df0a is byte-identical to 3c769c6d's
  (checked with `diff -r` on my pod), and I used my f271e422 build of it. **The same merge decision stands:** main's
  verifier cannot parse the `public s t f` line.
- All 3 proofs are accepted with the producer's expected counts: 976 slots, 2694 msgs, 9491200 bytes, 11666 rows. Each takes
  0.74-0.99 s at 15 threads on my 16 vCPU pod.
- The new circuit (485 columns, depth 1, a merged LK table), epilogue and chain are byte-identical to ab57df0a's
  `gpu.nvf4.circuit export` run on my pod. public.bin equals main's frozen `instances_fp4(4096)` (s, t, f), with 0 rows
  mismatched. The circuit builder (gpu/nvf4/circuit.py plus the prover changes) is not on main.
- Negatives, all rejected: `mutate --sample 24` (148/148), my s/t/f edits, and the public line reordered or removed. The same
  binary still accepts the FP8 y16 proof.
