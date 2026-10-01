---
lane: circuits-build-speed
kind: report
created: 2026-10-01T00:04Z
status: open
---

CHECKPOINT 816fe3d02 (01:01Z) [open] 6:01 PM PDT: branch 250ef6193 (scheduling+GC+manifest beside compose; refs hunk dropped, it is #517's) builds the B8 1024/128 ref row in 328 s (baseline 442 s), all program/workload/manifest digests equal (r20261001-005319-e28e vs r20260930-235343-09de); next: +#517 run, compose/load profile
CHECKPOINT 86ff83193 (00:37Z) [open] 5:37 PM PDT: GC tuning for build/global-program committed (dc0df3eda; envelope derive 203->173 s, same digests, r20261001-002750-caee); combined after-run r20261001-003720-bd76 running; next: overlap manifest with compose
CHECKPOINT 352d8dcf2 (00:18Z) [open] 5:19 PM PDT: baseline B8 1k/128 Build 442 s (r20260930-235343-09de), B1 256/32 95 s (r20261001-000359-9339); envelope derive profile r20261001-000345-89b1 (refs slice 30%); pushed a62ee2a30 (compose+manifest no longer wait on the envelope derive), measuring r20261001-001838-3673
CHECKPOINT e3ea0c9a0 (00:04Z) [open] 5:05 PM PDT: baseline on main e3ea0c9a, reference B8 1k/128 config-run Build = 442 s (r20260930-235343-09de; 6-wide auto; digests = cov-k20 of record): envelope derive 332 s is the floor, compose tail 56 s + manifest 49 s wait on it. Next: decouple compose/manifest from the envelope, profile the envelope derive.
