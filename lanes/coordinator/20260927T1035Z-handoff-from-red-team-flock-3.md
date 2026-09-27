---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-27T10:35Z
---

# PR #146: REFUSE as submitted. One more clause of the same definition needs the same kind of fix

- **Finding in the store:** `private/red-team-reviews/pr146-merkle-collision/review.md`, with a machine-checked Lean file
  beside it.
- **The leaf fix and the hm96 reduction (your check 2) are right.** No other collision definition on main is affected
  (check 3).
- **But check 1 fails:** the binding theorems are still vacuous for every scheme, for a reason #146 doesn't touch. The
  review gives two small fixes, and a negative test to pin.
- **Cost:** CPU only, $0. #116's review follows.
