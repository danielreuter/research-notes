---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: red-team-flock-3 · kind: handoff · from: refinement lane (bc-159ce83b) · to: red team (bc-f0bc7e75) · created:
2026-09-28T16:06Z · repo: danielreuter/verity · about: #296, correction to my 15:48Z note: the live game is now the
server's single loop

# #296: the live game changed; the pin didn't

**What changed.** At `e13ad134`, #296's live game is the coin server's loop rather than an interleave of two streams.
`liveRounds dg N acc` is `.send (Option Submit)`:
- a `Submit` names its rep's stream, the framed bytes and the coin count `n`;
- on `some s` it draws `.coin (Fin s.n → 𝔽)` at once and appends `roundOf dg s.bytes s.n c` to that rep's stream;
- on `none`, or after `N` rounds, it stops.

`liveTable` is `root_B`, the link points, `liveRounds dg N ([], [])`, then the proof files.

**So the "stronger prover" paragraph in my 15:48Z note no longer applies.** The live game is the server's protocol as
written: one submission at a time, its coins drawn before the next.

**Why:** the simulation (R11c) now follows one loop on the live side, choosing the round's rep in the model's
`interleave`. With an interleave on both sides, it would have had to follow both games' unfolding at every step.

**Unchanged:**
- `Sim`, `Sim.strategy` and the pin `Sim.prob_le`, so its review stands as described;
- the audit (PASS, 32 pinned theorems);
- N1's any-schedule lemma still isn't needed.
