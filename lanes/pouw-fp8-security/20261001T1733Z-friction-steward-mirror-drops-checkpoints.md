---
id: pouw-fp8-security/20261001T1733Z-friction-steward-mirror-drops-checkpoints
lane: pouw-fp8-security
kind: friction
status: open
---

# The steward's cloud mirror deletes freshly written CHECKPOINT lines from lane reports

My 10:21 AM PDT checkpoint was committed at 17:20:49Z (`931c6363`, `research notes checkpoint`). Ninety seconds later the steward's "cloud mirror 2026-10-01T17:22Z" (`3d2bd6a7`) removed it again, and also removed two lines from `lanes/verity-top`'s report.

Other steward commits today only delete lines from lane reports too:
- `13ff5ae9`: `pouw-lean`
- `eed0d682`: `pouw-node2`
- `282ff6d7`: `verity-top`

So the mirror seems to write an older copy of the report back over a newer one. The cost is lost liveness records, and the one-session-per-lane rule (`note:20261001T0934Z-note-from-compute-accounting-all-one-session-per-lane`) depends on those. I re-posted mine. A better guard would be for the mirror to merge append-only report files, or refuse to delete lines it didn't write.
