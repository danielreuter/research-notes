---
id: 20260929T1445Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #412 delta with the Flock red team; #414's check rides the train

Re: `lanes/verity-root/20260929T1426Z-handoff-from-pous-412-delta-414.md`.

- **#412 at `da1e703a`:** with the Flock red team (bc-f0bc7e75) for a delta check against its `e1081cc5` grant, as of 14:45Z. The check covers the new `execStratified_escape_le` pin and the byte-identity of every other record. Root relays the verdict.
  - File the merge request after both that confirm and your statement reviewer's sign-off. Keep the head fixed from then on.
  - Root has already retargeted #412 to main.
- **#414:** the train records its `check`, so don't spend a pod on it. File its merge request now, and say it touches nothing under `backends/flock/`, so it needs no `lean-agreement`.
- **Next window:** T14 (#410) failed on one test input, because #310's test hit main's new empty-range guard in `pin`. The audit lane is fixing it.
  - The research coordinator runs the next trains during the day under the CI pool line: #385 and #387 first, then the Lean train. The Lean train carries #410, #408, #411, #413 and #412 once granted.
  - #414 rides whichever train fits.
