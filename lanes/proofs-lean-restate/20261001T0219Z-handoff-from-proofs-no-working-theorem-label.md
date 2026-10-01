---
id: 20261001T0219Z-handoff-from-proofs-no-working-theorem-label
campaign: verity
lane: proofs-lean-restate
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72), on Daniel's ruling with lean (~7:17 PM PDT), relayed by the top-level
---

# Daniel withdrew the "working theorem" label: condition 5 is now "every hypothesis is a listed assumption with its kind"

to: proofs-lean-restate (bc-3b607340), red-team-flock-3 (bc-f0bc7e75); the same note is in both lanes. Re
`note:20261001T0214Z-reply-from-red-team-flock-3-restatement-verdict-5fd065ef`, condition 5.

- **The ruling (Daniel, with lean, ~7:17 PM PDT):** lean's fifth answer is withdrawn. There are only theorems and
  assumptions, and a theorem is proved under its assumptions. No text calls anything a "working theorem".
- **What the `_hm96` headlines (and `Prog.flock_headline`) are proved under:**
  - `cr/sha-512` and `ecr/sha-512`;
  - the internal facts they take as hypotheses: `HmRowComputes`, the derived column placements, and the constant and zero
    columns.
- **The footprint line** in the review, `ASSUMPTIONS.md`, the README, `e2e-checklist.md` and the PR body lists every one
  of them as an assumption, with its kind:
  - hardness (`cr/sha-512`, `ecr/sha-512`);
  - platform (A3, the coin server's OS randomness);
  - model;
  - or something we intend to prove (`hHm`, `pp.placed`, `pp.aliased`, `lay`, `rs`, `tr`, `hConst`, `hZero`).
  There's no separate label.
- **Condition 5 changes accordingly.** Writer: drop any "working theorem" wording you've added and write the kinds instead.
  Reviewer: check the kinds in place of the label.
- **Lean's other answers stand,** and so do conditions 1–4 and my 7:18 PM PDT call on condition 6
  (`note:20261001T0218Z-handoff-from-proofs-condition-6-legacy`).
