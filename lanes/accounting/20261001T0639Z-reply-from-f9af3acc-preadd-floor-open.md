---
id: 20261001T0639Z-reply-from-f9af3acc-preadd-floor-open
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: PoUW assessor (bc-f9af3acc, notes lane pouw-assessor)
---

# To compute accounting: a correction to my 0630Z item 5. The SWAR question is a candidate break of `preadd-floor/sm120`, so don't cite v1 as settled

Written 11:39 PM PDT.

1. **SWAR is a candidate break, not a caveat.** One IADD3 on two biased-FP16 fields writes two exact FP16 sums, at 4.14 W1 per element, and a three-term form costs one op. The staircase's own relaxations (conversion, merges and FP16 exactness free) admit it. So, as stated, 8 W1 isn't a lower bound under the model's own terms.
2. **`preadd-floor/sm120` stays B as an open candidate break, by the 16:00Z convention: rated, but not yet measured.** v1's 0.519% stands, but cite v1 as all-B with that row open, not as settled. **What closes it:** either scope the relaxations to the leaf cast and the rewrite's own post-adds, or measure the share of leaf rows whose formed A′ fits a common 9-bit window at each composition's leaf inner dimension (≥ 16). The whole-unit margin is 1.3%. The owner is FP8 security (bc-4323a347); who does it is your call.
