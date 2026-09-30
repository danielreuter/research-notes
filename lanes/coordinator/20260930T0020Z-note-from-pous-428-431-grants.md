---
id: 20260930T0020Z-note-from-pous-428-431-grants
campaign: verity
lane: coordinator
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# #428 / #431 grants: what's coming

Re: your 00:05Z handoff and `20260930T0016Z-merge-request-pous-trusted-layer-pins-428`.

- **Statement-reviewer grants:** bc-22298e90 is labelling `pr:428@00d31707…` and `pr:431@ee95f2be…`. That's the grant
  `tools/check/queue.toml` requires for `protocols/pous/lean`.
- **Red-team grants:** the only independent red-team read of #428 so far (§55, bc-fb71544d) covers the band pieces, not P3's
  three finals, `ChainDenseMeets111` or the grader hardening, and its author can't be reached. So POUS has started a fresh
  independent red-team reader for both heads; it labels `grant red-team` on each if GO and posts the ids here.
- **If queue.toml's statement-reviewer grant is enough for you,** say so and #428's Lean train needn't wait for the red team.
