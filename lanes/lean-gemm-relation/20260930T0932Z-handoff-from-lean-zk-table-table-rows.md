---
lane: lean-gemm-relation
kind: handoff
from: lean-zk-table
created: 2026-09-30T09:32Z
---

# lean-zk-table: rows for the security theorem table (`theorems.md` §4)

These rows are for `internal/lanes/lean-gemm-relation/theorems.md`, which is yours. Add them to §4 after the #245 row. The
"Theorem Z" row stays a paper proof, but its Lemma B and Lemma A now have Lean instances.

- **Records** are the first 8 hex digits of `type_hash` in `soundness/lean-audit.json` at #519's head `980326ef`.
- **Status:** all 0 `sorry`, awaiting red-team-flock-3's statement grant.
- **Audit:** `r20260930-090944-bc3a` (PASS at `1aba1da1`, 8 of the 9 pins); `r20260930-093147-9dc8` (at `980326ef`,
  running).

| Theorem | What it says | Status | Assumptions | Record |
|---|---|---|---|---|
| `FlockSoundness.ZK.Table.table_shvzk` | Lemma B (SHVZK with the final message) for one masked table at a fixed non-degenerate coin vector: the spec-level reference prover's view (`Table.view`: every pre-final and final message, hm96 leaves opened or ideal, world `W₁`) and `S_shvzk(x, e)` (`Table.sim`, §3.2) have the same distribution | proved, pinned in [#519](https://github.com/danielreuter/verity/pull/519) | none cryptographic, exact in `W₁`. Hypotheses: non-degenerate coins (`Rank`, `W^r` bijective, `β ≠ 0`); T4 at the opened positions (`PadOnto`, `PadsOnto`, discharged below); H_reg; `InnerHolds` (row (xi): the honest pads satisfy the inner proof's constraint) | soundness, `36891e19` |
| `…ZK.Table.table_prefinal_translate`, `…table_prefinal_indep` | Lemma A in `W₀`: for any two witnesses carrying the region data, a translation of the blocks `u`, `R`, `h`, `μ` (each by an amount reading only earlier blocks) maps one pre-final view to the other, so they are equally distributed (`card_fiber_eq_of_triShift`) | proved, pinned in #519 | none. Hypotheses: `Rank`, `W^r` bijective, `β ≠ 0`, H_reg | soundness, `53c48963`, `0de0f97d` |
| `…ZK.Table.star`, `…ZK.padColumn_honest`, `…ZK.Table.inner_complete` | (★): the extra lanes are determined by the other openings. Completeness: the honest padded level 0 read through `Model.padColumn` is the codeword of `y₁'`, and the masked verifier's inner check passes | proved, pinned in #519 | none (`inner_complete`: `InnerHolds`) | soundness, `d04592d7`, `deaf0ad9`, `924fa7ee` |
| `…ZK.padOnto_M1`, `…ZK.padsOnto_monomial` | T4 for M1's level-0 padding and for the pads code: the paddings reach every vector of opened values | proved, pinned in #519 | **`PadNonvanishing`** (`X_L + κ ≠ 0` on the level-0 domain, `Assumptions`) for `padOnto_M1`; `A.Correct` | soundness, `b2ef29e5`, `25c4d6df` |
| `…ZK.ideal_leaf_swap` | T1: swapping one hm96 leaf for an ideal one changes any event's probability by at most `δ₁` | proved, pinned in #519 | **`Hm96Hiding`** (HDK: hm96's `δ₁` at the pinned key, `Assumptions`) | soundness, `55ff95d4` |

**Gap lines for the morning report.** These replace "Nothing in Lean covers … Theorem Z itself":
- Lemma B holds exactly in Lean in the ideal-leaf world.
- The lift to real leaves (T1 once per hidden leaf, `2·δ₁·N_hid`), the Goldreich–Kahan hybrids, T6's extraction and T7's
  generating function stay on paper.
- The clear protocol's completeness (zerocheck, lincheck, ring switch, Ligerito on `y₁'`) is not in Lean. The model
  takes the clear values as parameters, so the ZK theorem holds for any of them.
