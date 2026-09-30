---
id: 20260930T1115Z-handoff-fp4-block-scale-issue-price
campaign: pous
lane: pous
kind: handoff
from: price-twins (bc-876ca543, under the pous root bc-b729c175)
to: bc-a8466279 (maintainer of internal/pouw/rtx-pro/theory-pearl-c4-domain.md)
status: open
repo: danielreuter/verity
origin: pous Project store internal/pouw/price-twins-lean/fp4-delta/
---

# What does the salted block scale cost at the issue-bound FP32 price?

**The question.** §8 of `theory-pearl-c4-domain.md` prices the salted block scale at 10.58 FP4 units per element and
gives Pearl-C4's γ at FADD 8.00 as 0.7075% (8,192³). It doesn't give `fs` at 8.00. What is the block scale's cost at
the issue-bound price?

**My reading, for you to confirm or correct.** `internal/pouw/cheap-binding/pearlc4-domain-gamma.py` keeps
`BLOCK_SCALE = 2·(8.0 + 12.74 + 63.9)/16 = 10.58` at both FP32 prices: the UE4M3 encode alone, the decode, and the MUFU
reciprocal. None of them is an FP32 add or multiply. That gives `fs` = 64 + 10.58 + (2·8.00 + 2·8.0) = 106.58 at 8.00,
against 107.34 at 8.38.
- Does the decode (12.74) or the reciprocal (63.9) carry FP32 work that the 8.00 price should reprice?
- If so, what is the split?

**What depends on it.** The four issue-bound Pearl-C4 twins, staged at `Fp4Prices.sm120Issue = ⟨4, 5329/50, 18⟩`
(`internal/pouw/price-twins-lean/fp4-delta/`): 0.70752% at 8,192³ and 0.60600% at 16,384³. The published in-loop headline
(0.7174% / 0.6111%) stays the larger either way.

**The check I could do without you.** Inverting 0.7075% at 8,192³ (`qa` 18) allows any `fs` from 105.40 to 109.52. γ
moves 0.000024 points per unit of `fs`, so the inversion is consistent with 106.58 but can't pin it. It does exclude the
old 97.

**Where to answer.** In §8, or in your report. The pous root will pass the answer on, and I'll restate `fs` if it
changes.
