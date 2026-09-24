---
lane: sp1-table
kind: handoff
from: coordinator
created: 2026-09-24T06:15Z
---

# Re: SP1 6.x is 100-bit: the frozen rule stands; record it exactly as you proposed

Acknowledged, and thank you for surfacing it with the source. The 2^-128 rule is frozen and the user is asleep, so no rule
change tonight: SP1 cells stay out of Table 2 and appear in D1/D2 with their security (target -100, achieved union-bounded
over shard proofs, source in the fingerprint). The morning report puts the decision to the user with the number beside it.
Keep everything else to the full contract so the cell is one decision away from rendering.

Optional, only after the A100 stock cell is registered and handed to verify-night: if SP1_TARGET_BITS_OF_SECURITY (or the
query count) is a source constant that the pinned GPU prover actually honours, a 128-bit re-parameterisation run is a
welcome extra D2 row, labelled "SP1, security parameter raised to 128 bits (otherwise unmodified)". Timebox it to 30 min;
if the GPU prover bakes the parameters in, write one line saying so and stop. Pass the same note to sp1-formats if it applies.
