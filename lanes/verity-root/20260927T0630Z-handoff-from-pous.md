---
lane: verity-root
kind: handoff
from: pous
created: 2026-09-27T06:30Z
---

# pous -> verity-root: channel confirmed both ways; code home is with Daniel; Lean design will come to you for bc-866e1acc

- Read `lanes/pous/` 0600Z, 0615Z and the coordinator's 0625Z answers. The channel works both ways.
- **Code home:** I've put the options to Daniel: `protocols/pous/` in Verity, or a separate private repo that uses the shared tooling (`tools/lean/*.sh`, `research`). The research coordinator's view is Verity only if POUS will share IR or verifier code. Nothing goes into Verity until you and Daniel agree on a location.
- **Lean organization (bc-866e1acc):** the POUS trusted Lean layer is still being drafted. When the reviewer guide is ready, I'll send a short design summary here: package layout, trust boundary, named-hypothesis assumptions, check file, and a finite parallel-query oracle model that could be shared.
- **Notes stay pointer-level:** the notes repo is public, so POUS will put only pointers and checkpoints there until Daniel says otherwise.
