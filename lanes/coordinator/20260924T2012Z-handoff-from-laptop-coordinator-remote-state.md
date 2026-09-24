---
lane: coordinator
kind: handoff
from: laptop-coordinator
created: 2026-09-24T20:12Z
---

# laptop coordinator -> Project coordinator: requirements for "remote state" (user chose option 2) are in campaigns/remote-state/REQUIREMENTS.md

The user approved option (2) and asked that everyone agree on the requirements first. I wrote them down from what I checked
on the laptop at 20:05Z. Two facts shrink the estimates you were given:
- The notes git repo is 14 MB. The 0.9 GB on disk is gitignored proof fixtures, which should go to R2.
- The catalog is already append-only immutable files with content-addressed remote keys, plus a disposable local index
  (`research data reindex --remote`). The work is to write to R2 at write time (the P0) and prove parity, not a new design.

One requirement was missing from the plan: the steward needs an always-on home. Please own the campaign, correct anything
in the file that is wrong, and launch the steps as lanes.

Housekeeping: `research notes status` still lists about 11 overnight lanes from 2026-09-23 as STALE (ajtai-leaf-2,
blake3-leaf-2, fp4-decode-2, hints-fused, ligerito-*, live-2b, live-2c, red-team-*). All of them are finished or were
succeeded by later lanes; they have no pods. Close them with `research notes checkpoint <lane> superseded` (or final) so
real stalls stand out. Some have dirty worktrees: save those to evidence before removing them.
