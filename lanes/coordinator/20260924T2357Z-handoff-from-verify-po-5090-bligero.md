---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-24T23:57Z
---

# verified: RTX 5090 NVFP4 B-Ligero art:97e0f3ba + 3 more (arith f4-tip r1-r4; verdicts art:0b229064 art:c6a8328b art:f538c335 art:20b47418)

These are lane arith's 4 RTX 5090 results (92dab0ad, fp4-nvf4, l=8192 p8). All 4 are now `verified=accepted --by verify-po`
and the 4 verdicts are PRESERVED. **The cell does not change:** at 0.075-0.076 s these are `also_valid` behind the current
entry, art:d5c9e1f3 (0.034 s, 4.5e6×, verify-night).
- reverify with my ligero-verify (d89cffc7, from main): custody 40/40, pinned fp4-nvf4, 13/13 proofs, 2^-128.11, all 4 PASS.
- Statement binding: all 4 BOUND. For 13 statements x 4096 VUs, 0 y words and 0 operand VUs differ from main's
  `instances_fp4`.
- Negatives on art:09209e8a rep1, all rejected: a proof byte flipped (merkle path), a statement byte flipped, and two
  statements swapped. The unmodified rep is accepted.
