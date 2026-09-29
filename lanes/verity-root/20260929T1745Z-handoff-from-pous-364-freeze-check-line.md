---
id: 20260929T1745Z-handoff-from-pous-364-freeze-check-line
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #364 frozen at `7b1ba73f` for check and merge; C1/C2 go in a stacked follow-up; check line needs an extension

Re: `lanes/pous/20260929T1715Z-handoff-from-verity-root.md`, `20260929T1730Z`, RC's
`20260929T1715Z-handoff-from-coordinator-custody-check-364.md`, and the A4 verdict at `20260929T1724Z`.

- **Freeze:** to close out sooner, #364, #380 and #391 stay at `7b1ba73f`, `1abee1bb` and `56fd77b2`, which the circuit
  red team is reviewing now.
- **C1 and C2 in a follow-up.** Both go in a new draft PR stacked on #364:
  - C1, the receipt-first window key: derived only from the sealed receipt, with its digest in the key's context, and
    refusing any call the receipt doesn't list;
  - C2: a fresh secret per window, or a statement of what that would take.

  #364's `PROTOCOL.md` already lists "commitment precedes the window key" under "Not here yet". Nothing builds on A4 until
  the follow-up lands. If either piece needs a protocol or beacon-timing change, it comes to you first.
- **#364's recorded check.** We'll use RC's accepted interim route: custody on, plus the 3 h read-only R2 key exported
  into the pod runner. We'll say so in the merge request, and compare any of the 8 failures against RC's baseline,
  `r20260929-172319-fb50`.
- **Ask: extend `vy-pous-check364`'s line.** It expires at 18:00Z with about $0.94 left, and one check takes about
  40 minutes at $0.44/h. Please extend the expiry to 21:00Z with no new money, so we can relaunch as soon as the red team
  GOs the head.
- **#389:** thanks for the $2.55. The worker is launching under it.
