---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: handoff · from: flock-soundness · created: 2026-09-27T15:30Z · re: Daniel's 14:34Z decision (expected-time collision resistance)

# #127 is ready for audit: A2 named, the link term of record set; the Lean plan is written and S1–S2 are in #163

**#127, [ready](https://github.com/danielreuter/verity/pull/127):** head `f117f52b`, retargeted to `main` (`5a7061c0`). It is docs plus one `Prop`.

- **A2 is named like BCHKS25.** `ASSUMPTIONS.md` §3 gains A2, and `Assumptions.SHA512ExpectedTimeCR` is the Lean `Prop`.
  - It is stated for one finder: a game with a fixed strategy, whose outcomes record the output pair and the evaluations made.
  - It can't be stated for all finders, because a finder that hard-codes a collision exists. So the link theorem will take it for the finder it builds from the prover.
  - Nothing uses it yet, and the axioms are unchanged.
- **The link term of record** is `t·N_s(8N₀/e)/2^256.5` (`DESIGN.md` §3). For audit B that is `t·2^-205.6`, or `2^-125.6` at `t = 2^80`. The strict-time and random-oracle rows are kept as comparisons.
- **Checks:** `lake build` (3926 jobs) and `tests/test_repository.py` pass. Both docs are under the cap: `ASSUMPTIONS.md` is 48,487 of 49,152 bytes.

**One thing for the audit.**
- **Why `8N₀/e` and not `4N₀/e`.** Main's previous option (i) row had `4N₀/e`. That value comes from a first-recovery value layer, which needs the committed transcript chosen by averaging over auxiliary extractions.
- **The record's derivation.** §3 now derives `8N₀/e` from the plurality value layer, as the lifetime doc §2 defines it. That is the form the Lean plan proves.
- **What moving costs.** Both bounds are sound, and they differ by one bit. Switching to `4N₀/e` would change §3's constant row and the plan's S4/S6, not the rest.

**The lifetime doc** (`docs/lifetime-soundness.md`) is updated with the headline first. I edited only the body; its frontmatter belongs to bc-1fcbe4c9 and is unchanged.

- **A material change for Daniel.** The link term now dominates the hash term.
  - At `2^-128` over a lifetime, `N·t ≤ 2^77.6` for audit B, and `2^65.9` to `2^87.2` over A–D. Before, it was `2^94` to `2^110` without the link term.
  - So at `t = 2^80`, one audit B already exceeds `2^-128`. At a `2^-100` target, `2^25.6` audits are covered.

**Lean** (the plan is `note:20260927T1510Z-draft-expected-time-link-plan`).
- **Done: S1–S2,** in [#163](https://github.com/danielreuter/verity/pull/163) (draft, stacked on #127).
  - The compiled bound's level-0 deviation now counts accepted runs only.
  - The extractor is written as the law of `k` accepted reruns (`Extract.expectAcc`).
  - `session_knowledge_sound_acc` proves `ε·Pr[fails] ≤ ε_c⁻ + N₀ε/(ek) + √(k·adv₀)`.
  - Standard axioms only.
  - No existing statement changes, so any #130 pin records reading `bad_pointwise` or `session_sound_of_table` are unaffected.
- **Next, S3:** the batched audit's analysis with this extractor, with a `c/(c−1)` scaling for the relative bound, and its count curve.
  - *Update 15:47Z: S3 is done* on #163's branch at `62cd2abd` (`analysisBE`, `flock_batched_countE`), with standard axioms only. The reruns are conditioned on the session accepting, not the one table, so that the relative term tracks the audit's own acceptance.
  - Pushed at 16:00Z (head `0ab7224d`, which adds the docs naming the proved pieces). The bundles I wrote during the outage, `artifacts/flock-expected-time-62cd2abd.bundle` and `…-0ab7224d.bundle`, are deleted.
- **Then S4–S6:** the link theorem.
  - The riskiest step is S5, the finder as one explicit game with its expected cost.
  - `ValueBinding` waits on M0's `hm96-sha512` layout only for its discharge, not for stating or proving the theorem.

**Documents.**
- Created: `internal/lanes/flock-soundness/20260927T1510Z-draft-expected-time-link-plan.md`, this note, and `internal/lanes/audit-lean/20260927T1535Z-handoff-from-flock-soundness-expected-time-link.md` (the interface change, for audit-lean).
- Updated: `docs/lifetime-soundness.md` (body), and `internal/lanes/flock-soundness/20260927T0705Z-draft-link-term.md` (a pointer line).
- Created then deleted: `artifacts/flock-link-options-f117f52b.bundle`. The push failed on the token at 15:11Z and went through at about 15:30Z.

**Not done.** `verity.claims` has no entry for A2. Only what a render cites belongs there, and nothing cites the audit's value layer yet.
