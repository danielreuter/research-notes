---
id: proof-service/20261006T0325Z-friction-steward-stale-sync
lane: proof-service
kind: friction
status: open
recurs: note:pouw-fp8-security/20261001T1733Z-friction-steward-mirror-drops-checkpoints
---

# A steward sync wrote a stale copy of a whole draft over a newer pushed one

The steward's "notes sync 2026-10-06T03:07Z" (`0bbbab4ff`) replaced `note:proofs/20261006T0255Z-draft-proof-service-interface`, pushed at 03:00Z in `84d2991a5`, with an older copy. The old 10:16 PM checkpoint came back, and the `timed` row and the prob_auditReg text disappeared. I restored it from `84d2991a5` and re-synced (`e8b9e7d49`, `4f62c536b`); about 15 minutes lost. This is the same stale write-back as the earlier note, but this time it hit a draft with a deadline rather than a report's checkpoint lines. The guard the earlier note proposes would cover both: refuse to write a path whose `origin/main` blob isn't the one the steward last read.
