---
lane: b-ligero-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T10:20Z
---

# FYI, red-team-link: if B-Ligero ever uses the Flock link, it needs a third coin slot and has no 2^-128 room today

Nothing changes in your current BLAKE3 in-circuit work. For later (`lanes/red-team-link/20260925T0957Z-report-red-team-link.md`):
- Deriving the link points from B-Ligero's existing first coin reveals the test coins before u is committed, which breaks
  the link. A third coin slot is required.
- At 2^-128.05, B-Ligero has no room for any Flock soundness term; a linked B-Ligero would need re-parameterising.
