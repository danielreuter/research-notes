---
lane: coordinator
kind: handoff
created: 2026-09-23T18:00Z
---
# red-team-leaf findings for blake3-leaf (full text: ~/.research/notes/lanes/red-team-leaf/20260923T1710Z-report-red-team-leaf.md, ## FINAL)
BLAKE3 keyed framing checked OK. NIT: `role` (x vs W operand) is not in the key: put it in the keyed-hash context string or the framed input
so an x-row and a W-row with the same words cannot produce the same digest. One line + a test.
