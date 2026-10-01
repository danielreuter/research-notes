---
lane: circuits-build-speed
kind: report
created: 2026-10-01T00:04Z
status: open
---

CHECKPOINT 352d8dcf2 (00:18Z) [open] 5:19 PM PDT: baseline B8 1k/128 Build 442 s (r20260930-235343-09de), B1 256/32 95 s (r20261001-000359-9339); envelope derive profile r20261001-000345-89b1 (refs slice 30%); pushed a62ee2a30 (compose+manifest no longer wait on the envelope derive), measuring r20261001-001838-3673
CHECKPOINT e3ea0c9a0 (00:04Z) [open] 5:05 PM PDT: baseline on main e3ea0c9a, reference B8 1k/128 config-run Build = 442 s (r20260930-235343-09de; 6-wide auto; digests = cov-k20 of record): envelope derive 332 s is the floor, compose tail 56 s + manifest 49 s wait on it. Next: decouple compose/manifest from the envelope, profile the envelope derive.
