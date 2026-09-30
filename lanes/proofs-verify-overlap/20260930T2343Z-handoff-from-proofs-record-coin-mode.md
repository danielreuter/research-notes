---
id: 20260930T2343Z-handoff-from-proofs-record-coin-mode
campaign: verity
lane: proofs-verify-overlap
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Record the coin mode in every point: M0's non-ZK default is seed mode (SHA-256 PRF coins), outside the "SHA-512 CR only" rule

Worker proofs-security found that `flock-circuit` turns on seed mode for non-ZK sessions (`live/src/bin/flock-circuit.rs:470`;
`coin_seed.rs`). The round coins come from a SHA-256 counter-mode PRF plus a SHA-512 commitment, which adds a PRF and hiding
assumption beyond SHA-512 CR. Daniel hasn't decided yet whether the benches switch to OS-random live coins.

- **Don't change the coin mode tonight** unless @proofs says so: the timing would shift mid-hillclimb.
- **Record it:** add `"coins": "seed-mode"` (or `"live-os"`) to every `hillclimb-point` record, and put it in `flags` as
  `coins-seed-mode` so the console badges it. Never compare points across coin modes.
