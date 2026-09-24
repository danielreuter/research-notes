---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-24T23:33Z
---

# verified: A100 BF16 B-Ligero art:5bcbf3fb + 3 more (arith a16-tip r1-r4; verdicts art:50b44dad art:68fa7c52 art:ce07f815 art:38410b93)

These are lane arith's 4 A100 results (92dab0ad, bf16-ampere-v3, l=16384 p8). All 4 are now `verified=accepted --by verify-po`
and the 4 verdicts are PRESERVED. After `reindex --remote`, the laptop Table 2 shows the A100 BF16 B-Ligero cell as
art:5bcbf3fb at 5.9e6×; the committed entry art:794365d3 (verify-night) is at 2.2e7×.
- reverify with my ligero-verify, built on my pod from main (d89cffc7): custody 76/76, pinned bf16-ampere-v3, 25/25 proofs,
  2^-128.05, all 4 PASS.
- Statement binding: all 4 BOUND. For 25 statements x 4096 VUs, 0 y words and 0 operand VUs differ from the frozen set my
  tree builds from the committed seeds (sha256 = manifest).
- Negatives on the dumped rep1 of art:61bc4902, all rejected: a proof byte flipped, a chain-end statement byte flipped, and
  the statements of sub-batches 0 and 1 swapped. The unmodified rep is accepted.
