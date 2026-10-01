---
id: 20261001T0048Z-handoff-from-proofs-review-object
campaign: verity
lane: proofs-lean-restate
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# The first-pass review OBJECTs to pinning your diff; seven changes before a pin

The fresh reviewer read your uncommitted diff (sha256 `e0eb3bdc…c209`, base `28174db56`, plus `Certificate.lean`). Its
verdict is at `note:20261001T0046Z-answer-from-red-team-proofs-restate-verdict`. The renames are sound, and dropping `hL1`
weakens nothing. Make these changes, then commit and push your branch (nothing is on origin yet):

1. **Strict CR is unused.** No theorem takes `SHA512CRStrict`, the `StrictCR.lean` the ledger cites doesn't exist, and
   `ksAvgBE`'s collision terms are unbounded. Either bound them under `SHA512CRStrict` or drop the ledger's claim.
2. **`δ_tree`** is missing from every end-to-end bound, including `Prog.flock_e2e_count` and `Prog.flock_e2e_drawn`.
3. **One headline.** State it over `p.circuit`, with SHA-512 as both `Hc` and `H`, at the executable's draw law, composed
   with A3. Its signature should show exactly SHA512CR-strict, SHA512CR-expected and A3, plus the open obligations as
   named hypotheses (W6 `placed`, `Layout.Aliased`, `HmRowComputes`, `hExec`, `hConst`, `hZero`, `vb`).
4. **Coins.** `ASSUMPTIONS.md` must say the statement is for live uniform coins drawn each round. Non-ZK M0 today derives
   them from one OS seed through a SHA-256 PRF, which is a third assumption. proofs-verify-overlap owns moving M0 to
   per-round OS coins. Until that lands, the headline is cited only for runs that use them.
5. **L1.** Word it as: "the headline bounds wrong units of the pinned rows circuit; 'computes the Definition' additionally
   needs `RowsCert` per template and the Definition's Boolean semantics in Lean." Daniel ruled at 5:22 PM PDT that every
   Definition becomes a Boolean circuit over AND/XOR/NOT (lane proofs-ir). Once that lands, a single generic
   Boolean-semantics lemma replaces the per-template `RowsCert`. Remove `hL1` from `e2e-checklist.md`.
6. **Retire the legacy items; don't rename around them.** That means `Refine.setup_wf` (the Blake3 path), `Refine/Live.lean`,
   `Soundness.lean`'s SHA-256 header, the frame-v3 tags in `Flock/Tags.lean`, and `verity/flock-tables` in Rust, Python
   and the README.
7. **Send the `audit.py --update` output to the reviewer** (red-team-flock-3 is the reviewer of record). Nothing is pinned
   before Daniel's yes on the L1 drop.
