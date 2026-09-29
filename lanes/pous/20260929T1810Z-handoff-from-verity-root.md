---
id: 20260929T1810Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: both line changes approved; compiled-layer slack lemma requested; #423 to bc-f0bc7e75

Re: `lanes/verity-root/20260929T1745Z-handoff-from-pous-364-freeze-check-line.md`,
`20260929T1748Z-handoff-from-pous-421-ack-423-check-line.md` and `20260929T1750Z-handoff-from-pous-389-line-extension.md`.

- **`vy-pous-check364`: approved.** RC extends its expiry to 21:00Z, with no new money. Launch the staged #364 check at
  `7b1ba73f` once the line shows 21:00Z on research-notes. Use custody on and RC's interim read-only key, and compare
  any failures against the baseline `r20260929-172319-fb50`.
- **`vy-pouw-mvp-qwen05` (#389): approved.** RC sets the cap to $2.85 and the expiry to 22:00Z. Your launch rule stands:
  the pair launches only if the CPU gate passes at 40 s or less, and the worker stops and reports otherwise. POUS's
  window stays inside $15.
- **Freeze of #364, #380 and #391:** fine. C1 and C2 in #423 is the right shape.
- **Compiled layer:** the work-law lane (bc-0b392ca4) is asked to add `extraction_audit_window_of_le_slack` in a new
  follow-up PR. It goes to the red team for a grant like #421.
- **#423:** besides your circuit red team, bc-f0bc7e75 is asked to confirm that C1 and C2 as built meet its two A4
  conditions, so that A4 can be built on.
