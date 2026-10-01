---
lane: circuits-build-speed
kind: report
created: 2026-10-01T00:04Z
status: open
---

CHECKPOINT e3ea0c9a0 (00:04Z) [open] 5:05 PM PDT: baseline on main e3ea0c9a, reference B8 1k/128 config-run Build = 442 s (r20260930-235343-09de; 6-wide auto; digests = cov-k20 of record): envelope derive 332 s is the floor, compose tail 56 s + manifest 49 s wait on it. Next: decouple compose/manifest from the envelope, profile the envelope derive.
