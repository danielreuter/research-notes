---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-27T21:35Z
---

# `FlockLevel3.build_computes` (cursor/flock-verifier-lookup-rows-7ab3 @ b7eb6a7e): GRANTED

As the named reviewer. The review is in the store at `private/red-team-reviews/m0-statement/review.md`, in the last section.
CPU only, $0.

- **The statement is what my lookup review needed.** A witness satisfying the verifier's own lookup rows, with the constant 1,
  has output bit `j` equal to bit `j` of `table[index]`, for every table.
  - It's stated over any characteristic-2 field, and uses the same table B side as the proved fold (L3-A).
- **Nothing is weakened.**
  - `useful ≤ KONST` is `2^48`-sized, so it excludes nothing real.
  - `build`'s preconditions are the verifier's own.
- **Pins:** one new pin, and no existing pin changed.
- **Checked independently here:** `lake build` passes, the lemma uses only standard axioms, and the level-3 audit passes
  (999 declarations, kernel replay, 50 pins).
