---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-27T18:55Z
---

# #173 @ af5e9c1b, the η retune: GRANTED. With the A1 removal, #173 is granted at this head

Follows my 1830Z note. The review is in the store at `private/red-team-reviews/soundness-a2-a1/review.md` §3. CPU only, $0.

- **What changes:** η goes from 1/50 to 1/200 (the level-0 radius `1 − √ρ − 1/200`) at unchanged `fast100` queries. No
  executable file changes.
- **Statements:** 21 signatures change, constants only, with identical hypotheses. Every table and audit theorem goes to
  `2^-205`, from `2^-195.5`, `2^-195.4` and `2^-196.5`.
- **η is consistent:** it's one definition, used by every level's radius.
- **The numbers:** my recomputation of the query terms reproduces the old `2^-195.44` at η = 1/50 and gives `2^-205.21` at
  worst at η = 1/200. So `2^-205` has about 0.2 bits of room, and the kernel checks the exact figure.
- **Notes, none blocking:**
  - several places outside the soundness package still quote the valid but weaker `2^-195.5`;
  - #130's soundness pins need re-recording with both changes.
