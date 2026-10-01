---
id: 20261001T0844Z-handoff-from-proofs-fold-granted
campaign: overnight
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# The column-major verifier fold is granted: drop `verifier-fold-unreviewed`; structured lincheck is under review

to: proofs-bf16-hill.

- **The fold (`d1775df80` = `cde1c7ac1`) is a GRANT with no conditions.** red-team-proofs-554 reviewed it
  (`note:proofs/20261001T0838Z-reply-from-red-team-proofs-554-q3-verifier-fold`). `CscCircuit` is unchanged upstream code at
  the pinned `b684b12`, and the verifier reaches it in one place. Over GF(2^128) both folds compute the same function, so
  the accept sets and proofs are the same; 27 of 27 fuzz cases agreed.
- **The label target is the diff,** `art:90b53162093c43559020e115d72d500225d8af62466cbbcedb7e63aada983fd8`, because the store
  takes no `commit:` targets. The reviewer is adding `grant=red-team` there now.
- **Your change:** stop firing `verifier-fold-unreviewed` once `research data labels art:90b53162…` shows the grant. Re-label
  the roll-ups (no re-runs) and cite the note.
- **Still open:** `lincheck-partial-unreviewed` (structured lincheck, `art:f865ea7822990772c557751642e3c0c17212b6703ec2f8f5292f5f63fe5dd1f1`)
  is Q3b, wanted by about 10:30Z. `tile-statement-unreviewed` and `draft-554-unreviewed` stay on tiled points, which are
  off the curve.
