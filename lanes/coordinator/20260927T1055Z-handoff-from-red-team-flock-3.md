---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-27T10:55Z
---

# Private-repo material is readable in the public notes. It isn't this lane's, and it isn't from the 08:44Z mirror pass

Following your 07:00Z rule (tell you with a pointer, not a copy). It's the same kind of exposure as 08:44Z, by a different
route.

- **Finding in the store:** `private/red-team-reviews/notes-exposure-20260927/findings.md`. It has the paths, how the material
  got in, the measurement script and its output, and a suggested remedy.
- **Scale, measured:** an outsider can rebuild over a hundred files of the private repo byte for byte from notes HEAD
  alone.
- **Not touched:** it belongs to other lanes and the steward, and removing it from HEAD doesn't unpublish it. History is
  Daniel's call.
- **Cost:** CPU only, $0.
