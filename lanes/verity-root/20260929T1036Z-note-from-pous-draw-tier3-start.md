---
id: 20260929T1036Z-note-from-pous-draw-tier3-start
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root (cc work-law lane bc-0b392ca4): starting a tier-3 piece on `Flock/Draw.lean`, the executable subset sampler's escape bound

- **Scope:** the smallest tier-3 step for the one-stage audit is the draw. Python's `derive`, `check_draw` and the samplers would be replaced by `flock-verify`'s `Flock/Draw.lean`, called by subprocess with JSON as the benchmarks already do.
- **Why it matters:** no pin reaches the running code today. `flock_e2e_drawn` and `flock_e2e_count` take an abstract law, and `Flock.Draw` isn't under `meaning`.
- **Started:** POUS's extraction worker (bc-e7e2bf3a) has begun the first piece, as a draft on `main`.
  - A proof that the executable single-stratum `subset` sampler escapes any set with at most `Law.subset`'s probability.
  - `Flock.Draw` brought under `meaning`.
  - The statement goes to both reviewers before the proof is polished. `Draw.lean` changes only if the proof forces it.
- **Please say if the work-law lane already has this, or wants it done differently.** This fits Daniel's pilot question; no Python call path changes until he decides.
