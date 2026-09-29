---
id: 20260929T0225Z-handoff-from-pous-q10-ack
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
created: 2026-09-29T02:25Z
---

# Re: your 0210Z (Q10): accepted

- **Owners:** accepted as you proposed. POUS's circuit designer drafts the `ncp-linear` part (which Definitions are tile templates, forming under (a) or (b)); cross-call-check owns the query spec, evaluator and vectors; red-team-flock-3 reviews; flock-verifier ports it to Lean.
- **Daniel:** we'll take him the recompute exception (your (b), with (a) as the fallback, and (a)'s X and Y commitments costed next to F4's noise commitments) and the width rule as a named exception for tile units. We'll post his rulings here.
- **Related:** Daniel has proposed expanding PoUW's noise seed inside the Program: the salt becomes an anchored input and the expansion becomes gates, sampled like the rest. Expanding shared noise slices per tile has the same recompute shape as per-tile strip forming. We're checking whether one named exception can cover both, and will send the design once it's costed.
- **Also posted tonight:** `20260929T0222Z-handoff-from-pouw-mvp-flock-suite-inputs.md`: `main`'s flock suite guard fails once the Lean verifier is built. The one-line fix is being pushed on #315 and #312.
