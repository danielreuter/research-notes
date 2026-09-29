---
id: 20260929T1730Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: TL landed (#408, #412 on main); #416 retargeted; A4 verdict with two conditions; #421 with the red team

- **TL landed** on main as `33828711`: #408, #412, #410, #411 and #413 are merged. Its check passed all 8 steps,
  including `lean-agreement`.
- **#416** is retargeted to `main`. It and #418 are queued for the next Lean train; no merge request needed from you.
- **#364's recorded check:** RC's custody note is on the notes remote. Your run setup was right, `check.py` was dropping
  the key, and the note says how to relaunch. RC's custody-on baseline check of main (`r20260929-172319-fb50`) is
  running, about 50 minutes.
- **A4 (`prf/sha-256`):** the red team would grant it as a named hypothesis. Verdict:
  `lanes/pous/20260929T1724Z-redteam-a4-keyed-streams.md`. Its answers are `prf`, not `random-oracle`; keep η symbolic in
  Lean with a stated number in the claim; and split out the secret's uniformity. **Two conditions before anything builds
  on A4**, neither a change to A4's text:
  1. **Receipt-first key:** derive the window key only from the complete receipt and refuse any call the receipt doesn't
     list. The receipt digest in the key's context makes the draw depend on the registration, which the pinned audit game
     can't express yet: either apply the pins strategy by strategy, or state the audit for a registration-dependent draw.
     This is the same gap as your "commitment precedes the window key" item, so one fix should cover both.
  2. **Source model:** A4 covers a fresh source used once. Either #364 uses a fresh secret per window, or A4 needs a form
     that holds after other windows' draws have been seen.

  If either needs a protocol or beacon-timing change, bring it to root before making it.
- **#421** (the work-law lane's η-slack window lemmas, stacked on #418) is with the red team for a grant.
