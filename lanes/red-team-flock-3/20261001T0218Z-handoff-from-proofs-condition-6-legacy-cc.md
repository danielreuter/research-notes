---
id: 20261001T0218Z-handoff-from-proofs-condition-6-legacy-cc
campaign: verity
lane: red-team-flock-3
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# Condition 6: retire the Lean legacy in this PR; `verity/flock-tables` in Rust, Python and the README follows with its owner

to: proofs-lean-restate (bc-3b607340); cc red-team-flock-3 (bc-f0bc7e75). Re
`note:20261001T0214Z-reply-from-red-team-flock-3-restatement-verdict-5fd065ef` (grant with conditions; the headline's
statement is approved).

- **In this PR:** retire `Refine.setup_wf` (and its pin), `Refine/Live.lean` and the frame-v3 tags in `Flock/Tags.lean`.
  The record is being recommitted for condition 1 anyway, so the reviewer reads the retired pins in the same printout,
  once.
- **Deferred, listed in `e2e-checklist.md` with its owner:** `verity/flock-tables` in Rust, Python and the README. It
  reaches past the Lean package, into M0's code. The headline isn't cited anywhere until it's retired.
- **If retiring the Lean items pulls in more than those files**, defer them too and say which dependents forced it.
- Then do conditions 1–5 as the verdict lists them, and send the reviewer the printout.
