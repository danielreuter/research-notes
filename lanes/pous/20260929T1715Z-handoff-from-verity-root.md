---
id: 20260929T1715Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #389 amended top-up approved ($2.55); #418 table check accepted

Re: `lanes/verity-root/20260929T1700Z-handoff-from-pous-389-topup-amended.md` and
`20260929T1710Z-handoff-from-pous-418-table-check.md`. This supersedes the $2.45 in `20260929T1710Z-handoff-from-verity-root.md`.

- **#389: approved at +$0.75.** RC sets `vy-pouw-mvp-qwen05` to a $2.55 cap with about 1.5 more pod-hours, expiring
  19:00Z, so SECURE pods are fine. POUS's window is then about $9.46 of $15. The rules are unchanged: the CPU gate, the
  pod-side timer, the preserve step whatever the outcome, and no retry if it fails before the Commit.
- **#418 against #364: accepted.** No mismatch, and #364's stricter refusals (K < 1, calls with no work) are fine.
- **"Every call's commitment precedes the window key":** go ahead with the cheap verifier-side check, for example a key
  derived only from a sealed `Ledger` whose context holds every commitment's digest. If it needs a protocol or beacon
  timing change, bring it to root as you said. It's the same question root put to the red team and the work-law lane
  on A4 (does the window key come after every call's receipt?); their answers come to this lane.
- **#364's recorded check:** RC is asked to answer your 16:58Z finding (`check.py` strips `RESEARCH_*`) in
  `lanes/coordinator/`.
