---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-24T22:07Z
---

# verified: RTX 5090 NVFP4 A-GKR art:fe57e68b (new Table 2 cell; verdict art:acf87c5c) -- needs agkr-nvf4's verifier change merged

This is lane agkr-nvf4's result (3c769c6d, fp4-nvf4, 1.044 s median), now `verified=accepted --by verify-po` with
`same_device=false`. Verdict art:acf87c5c is PRESERVED.
- **Decision for you:** main's `verity-gkr-verify` cannot parse this statement, which has 3 public words per VU. I verified
  with lane/agkr-nvf4 @ 3c769c6d's verifier: `git diff ab9573fd 3c769c6d -- backends/gkr/verifier`, +30/-13, an optional
  `public <cols>` line in chain.txt. I reviewed that diff and found it sound. The binding is symmetric in the functional and
  the claim, and the default `public y16` leaves old statements unchanged; the same binary accepts the FP8 y16 proof
  art:89a2ce85. I built and tested it (8/8) on my pod. Merge that verifier change (agkr-fp8 has the same change pending),
  or the cell rests on an unmerged verifier.
- All 3 proofs are accepted with the producer's expected counts. The circuit files are byte-identical to 3c769c6d's
  `gpu.nvf4.circuit export` run on my pod. public.bin (s, t, f) equals main's frozen `instances_fp4(4096)` final words, with
  0 rows mismatched; the digest d2d65f65… matches the result's.
- Negatives, all rejected: `mutate --sample 24` (148/148); my s/t/f edits; the public line reordered or removed.
