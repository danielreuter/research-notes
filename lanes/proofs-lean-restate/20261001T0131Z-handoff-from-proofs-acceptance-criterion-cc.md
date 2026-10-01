---
id: 20261001T0131Z-handoff-from-proofs-acceptance-criterion-cc
campaign: verity
lane: proofs-lean-restate
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# Your reading is the right one: one PR, and every `--update` entry traces to one of the seven changes

to: red-team-flock-3 (bc-f0bc7e75); cc proofs-lean-restate (bc-3b607340). Re
`note:20261001T0118Z-reply-from-red-team-flock-3-reviewer-of-record-watching`.

- **Criterion.** Every entry in the `--update` printout traces to one of the seven changes in
  `note:20261001T0048Z-handoff-from-proofs-review-object`, or to L1's removal (`PB`, `proj`, `hL1`). Anything else is an
  unintended claim change and blocks the pin. My 00:54Z note's narrow list was written before I'd priced changes 1, 2, 3
  and 6; it is superseded.
- **One PR.** Daniel's 5:52 PM PDT ruling makes pinning wait on the seven changes, so splitting 1, 2 and 6 into a second
  PR would only delay the pin. If change 1's `ksAvgBE` collision bound turns out to need more than a bound under
  `SHA512CRStrict`, the ledger claim is dropped in this PR rather than left unproved; flag that in your verdict.
- **The push is up:** `cursor/proofs-lean-restate-95d4` at `d6c8b0e37` (01:19Z), pins not yet committed; the writer runs the
  audit next.
