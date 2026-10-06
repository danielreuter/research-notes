---
lane: red-team-defs-move
kind: report
created: 2026-10-06T02:39Z
status: final
---

CHECKPOINT none (02:53Z) [final] GRANT both (Arith.Correct, RepDoomedW): old+instField->commRing rewrite hashes to the new records, kernel-defeq; note red-team-defs-move/20261006T0252Z-finding-defs-move; art:98514134; run r20261006-023815-a5d6; label on r20261006-004654-ea26
CHECKPOINT none (02:39Z) [open] started: art:6059ec16 fetched; rewrite_check rerun PASS (8 sites); record diff: only the 2 defs differ among 4446 read by the 201 guarantees; rebuild+kernel probe r20261006-023815-a5d6 running

## FINAL

~~~text
tip: none (red team; no branch, no commit to verity)        merge-with: none
known-failures: none    pod: none of mine (shared vy-nebius-1, one run); $~2 est.
artifacts: art:98514134a98ab2ea3b46a01ff2a6e6d6bfe39ca42d019f93b716eeff42927900
~~~

Verdict GRANT on "meaning unchanged" for `FlockSoundness.Model.Arith.Correct` and `FlockSoundness.RepDoomedW`; finding
note red-team-defs-move/20261006T0252Z-finding-defs-move; run r20261006-023815-a5d6; label `note defs-unchanged: GRANT
(red-team-defs-move) …` on r20261006-004654-ea26 (2026-10-06T02:52:54Z, ref art:98514134), beside lean's. Inbox: nothing
received.
