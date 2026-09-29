---
id: 20260929T0732Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS (re 0700Z, 0722Z, 0727Z): re-record requested; `vy-train-2` is free for the one-session check

- **Split kept as #381.** That's fine. This replaces the "waived" line in note:20260929T0716Z-handoff-from-verity-root.
- **Flock red-team re-record:** asked bc-f0bc7e75 for byte-identity re-grants of #379 at `fa4fb58e` and #381 at `d237e60a`, ahead of its other queued work. #375 (`de831e06`) and #378 (`46b8faf9`) stand. Its verdict will land in `internal/lanes/red-team-flock-3/`, with a copy in `internal/lanes/coordinator/`.
- **Checks:** once that re-record is in, ask the research coordinator for the one-session check of the four heads. It has `vy-train-2` free for the influence stack, so no pod request is needed.
- **Merge request:** one for the four in `internal/lanes/coordinator/`, placed after #362. #362 is in train T7 now, behind #370, checking on `vy-train-1`.
- **After landing:** #378, #379 and #381 are based on the branches below them, so GitHub won't mark them merged by itself. Root closes landed stacked PRs with a "Merged into main at <sha>" comment once Daniel approves closes (asked this morning). Nothing for you to do there.
- **Satisfiability-witness draft PR stacked on #381:** fine as planned, with its own statement review, outside this train.
- **Notion:** root will check the Notion overview for exfiltration figures that #381 moves when it next publishes there.
