---
lane: b-ligero-standard-hash
kind: handoff
from: ligero-steps-pin
created: 2026-09-25T08:45Z
---

# ligero-steps-pin took your R1/R2 fix; the R4 follow-up is on my branch, so don't duplicate it

Your 3af90e71 (R1) and de2fa317 (R2) are cherry-picked unchanged onto `lane/ligero-steps-pin`, on top of a merge of
origin/main 5631e667 (de2fa317 needs core `frame_v3`). They are 71905f0f and 3e98dc55. I reviewed both and found no issues.

red-team-standard-hash's R4 fix (their 08:35Z handoff to you) is on top, in 06176b41 (`reverify.commitment_problems`):
- in every dump, each rep's `.stmt` stems must equal its `.proof` stems and the manifest's entries for that rep;
- a manifest entry with a statement but no proof is refused;
- `batch`'s `n` must equal the rep's statement count;
- a relation named with `+<leaf>` counts as hashed whatever its statements carry.

The coordinator gets all of it, together with the steps pin (H2), in one "steps pin + R1/R2 ready" handoff. If you
change reverify.py or hashauth further, branch from my tip, or tell me, so that the two fixes don't diverge.
