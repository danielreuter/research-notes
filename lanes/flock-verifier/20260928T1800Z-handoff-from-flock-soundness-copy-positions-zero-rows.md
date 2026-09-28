---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-verifier · kind: handoff · from: flock-soundness (bc-9e538dc5) · to: flock-verifier (bc-8e519ca0); cc
audit-lean (bc-a0c5a22f), M0 (bc-ff572e70), the research coordinator · created: 2026-09-28T18:00Z · repo:
danielreuter/verity · re: `flock-verifier/20260928T1630Z-handoff-from-flock-soundness-dp-1e-interface.md`

# N1 goes into the model: #308 and #313 hold. From 1e, each slot input's copy position and the forced-zero rows

**The decision.** N1 is option (b) (`flock-soundness/20260928T1750Z-plan-n1-repeated-and-zero-sources.md`). The program
model admits one source feeding several inputs of a unit, and a constant-zero source. So the verifier and the attention
template stay as they are, and #308 and #313 don't merge (the research coordinator's call). M0's padded attention, with a
zero-leaf `b` and one tail port into eleven inputs, is covered.

**What I need from 1e,** beside the 16:30Z items, for audit-lean's `TableClass` (its handoff
`audit-lean/20260928T1800Z-handoff-from-flock-soundness-copy-positions-zero-rows.md` has the exact shape):
1. **Each slot input's copy position,** read from the accepted statement's Δ:
   - a leaf input copies bit `w % 16` of row word `w / 16`;
   - a wired input copies its source port's position;
   - a zero leaf copies the slot's forced-zero row (`base + useful`);
   - a wide leaf cut's bits 16 and up copy the range's first slot's `zero` row.
2. **The forced-zero rows' positions,** where A and B are 0.

Both are facts about what `HmRow.delta` and the typed Δ already write. No verifier check changes.
