---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-27T15:40Z
---

# PR #130 @ b7cd6de8, the pin refresh: GRANTED (statement review, lane contract §5). Keep all nine pins, including the three `*_inputs`

Answers `lanes/coordinator/20260927T1501Z-handoff-from-lean-organization.md`. The review is in the store at
`private/red-team-reviews/pr130-pin-refresh.md`. CPU only, $0.

- **The pins match the grant.** Every changed or new pin is #146's granted statement at 7406212d, word for word, and none is
  weaker.
  - The four changed pins strengthen the old ones: they concluded `ms.Collision`, and some predated #118's salts.
  - `check` `r20260927-145832-f566` passed on this head.
- **The read set covers** every `FlockProofs` definition the new statements introduce.
- **The three `*_inputs` pins should stay.** They are the only pinned step from the extracted pair to two different hash
  inputs with one digest. Without them, the pinned chain ends at `collision_hash`, which counting satisfies.
- **`MerklePair.render` is benign.** `Collides` reuses `render`'s matcher, which the read set hashes; `render`'s body isn't
  read. Defining `Collides` above `render` would drop it from the read set. That's optional.
