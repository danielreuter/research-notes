---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-25T00:17Z
---

# verified: H100 LIVE (D3) x12, 4 configs x r1-r3 (d3-h100, main 1d9c3198; verdicts art:e13419b4 … art:41e3a98b)

These are lane d3-h100's 12 live-verifier results, now all `verified=accepted --by verify-po` with 12 PRESERVED verdicts.
**Table 2 is unchanged:** after `reindex --remote` all 12 are `also_valid`, and the H100 cells are still art:e3362256,
art:709ab20c, art:c09947fd and art:2e7baba7. They serve as D3 evidence. The render's drilldown doesn't cite them yet; wiring
them into D3 is d3-h100's job.
- reverify from my tree (the verifier-relevant sources equal main 1d9c3198's; only tools/research differs) with my ligero-verify
  d89cffc7, on the dumped rep 1 with the live verifier's coins. All 12 PASS:
  - bf16-hopper-v3x4 and bf16-hopper+hash: 76/76 custody, 25/25 proofs, 2^-128.05
  - fp8-hopper-v3x4: 40/40, 13/13, 2^-128.33
  - fp8-hopper+hash: 40/40, 13/13, 2^-128.32
- Statement binding: all 12 BOUND, with 0/4096 y words differing. For the v3x4 statements the operands were also compared
  (0/4096 differ). The +hash statements carry no operand words, so only y is compared there.
- Negatives, all rejected: on L-f8b-r1 (art:d0ada343) and L-b16h-r1 (art:585e4182), a proof byte flipped, a statement byte
  flipped (on the hash tree: "auth: y: multiproof rejected"), and two statements swapped. Both unmodified reps are accepted.
- Verdicts in the handoff's order: art:e13419b4 art:209fdd63 art:ed310632 art:d0aeef7f art:fe61cce4 art:f765ab6c art:649e27ed
  art:0b754787 art:1e442d10 art:cc7fa7cd art:549ee1d3 art:41e3a98b.
