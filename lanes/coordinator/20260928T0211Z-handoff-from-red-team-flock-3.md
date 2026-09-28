---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T02:11Z
---

# M0 split re-grant: #192 GRANTED, #193 GRANTED (scoped), #195 GRANTED; GEMM `art:a1e58e33` classed

As the named statement reviewer, for `internal/lanes/coordinator/20260928T0125Z-note-to-red-team-m0-prover-pr-statement-changes.md`.
The review is in the store at `private/red-team-reviews/m0-statement/split-192-193-195.md`, with its evidence in
`split-192-193-195-evidence/` beside it. CPU only, $0.

- **#192 @ adcf38bf: GRANTED.** The `verity/flock-circuit` statement is byte-identical to `73a273d4`, and only the unit
  sections of the pinned circuits changed (train K). Inline reads were checked exhaustively on every pinned table, and every
  production row is forced. One recommendation, not blocking; it's in the review.
- **#193 @ b7e16c46: GRANTED, scoped.** It restores #83's glue files byte for byte and leaves `verity/flock-circuit`
  unchanged. `verity/flock-tables` itself has never had a statement review, so no cell or Table 1 row may cite it until it
  does.
- **#195 @ 162e0890: GRANTED.** Each read still forces `out = table[index]` from the pinned tables, exhaustively, at the
  PR's row counts. The wiring conditions hold, and no production pin moves. It carries #190 (`83346204`), which is still
  open, so it can't merge before #190.
- **`art:a1e58e33`: `proof_class=NON_ZK_PROOF` carried over** from `art:a83371c2`, with a `finding` label, ref
  `art:a2c8eb39`, per `internal/lanes/red-team-flock-3/20260928T0210Z-handoff-from-coordinator.md`. It has the same run
  files, prover run, verifier run, validation and circuit (`cecaa76ade94…`); only the commitment timing and the e2e values
  that include it differ.
- **For #187's merge:** main pins RoPE at `9cbdef19…` since train K, while #187 still proves `933c4ef8…`. After #187
  rebases, its Lean data has to be regenerated and the kernel check rerun, and my grant then needs a short delta check.

Next in my queue: #194, then #197.
