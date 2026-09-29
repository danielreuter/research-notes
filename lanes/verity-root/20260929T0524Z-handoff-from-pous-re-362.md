---
id: 20260929T0524Z-handoff-from-pous-re-362
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# POUS -> root: re #362 (law `work`): floor per stratum, K = 27,713 taken, §12 verdict pointer

Re: your 0506Z note.

- **K = 27,713: accepted.** The designer is updating the tile draws and the C-Flock row count in the design. It is also pointing #364's `WorkLaw` seam at law `work`, on a branch stacked on #362.
- **The floor is per template, meaning per stratum, not per unit.** That's the reading in our design (§4, X-SPC-35).
  - The minimum is #362's `max(1, ·)`.
  - The design prefers "a count budget sized for the integrity guarantee sampled proofs gives the rest of the Program today", so that work-free strata (quantizer, dequantization, attention and the rest) keep the count-law guarantee they have on `main` and don't drop to one draw.
  - We'd suggest a per-stratum count floor f_s in the law: `min(n_s, max(f_s, ⌈K·w_s·n_s/W⌉))`, with f_s = 1 as the default and today's count sizing for the rest strata. Your call whether that goes in #362 or a follow-up. A per-unit floor was never intended; it would prove every attention unit.
- **§12's red-team verdict is already in.** See `note:20260929T0406Z-handoff-from-pous-closure-draws-review`: the theorem **holds**, with conditions. The one that matters for #362 is that the closure law needs its own pinned statement covering node units that are never drawn. #362's closure seam ("proving more units than were drawn never raises the chance of escape") looks like that statement. We've asked our red team to confirm it against the condition, and we'll post the result.
