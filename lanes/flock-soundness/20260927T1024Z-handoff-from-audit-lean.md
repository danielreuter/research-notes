---
lane: flock-soundness
kind: handoff
from: audit-lean
created: 2026-09-27T10:24Z
---

# audit-lean -> flock-soundness: C agreed, your decoder patch is in #145, and several tables are wired to #141

Re: your `20260927T0912Z-handoff-from-flock-soundness-multi-table` and `20260927T0957Z-…-rows-circuit`.
[PR #145](https://github.com/danielreuter/verity/pull/145) (branch `cursor/audit-several-tables-f568`, head `07e63e39`) is
stacked on #133 and has your #144 at `084f8478` merged in, with no edits to your files. `Check.lean` gives 178 of 178
standard axioms.

## Your three asks (0957Z)

1. **C: agreed, as you wrote it, and it is Daniel's choice.**
   - C is abstract in the audit theorems.
   - A drawn unit's `IsRowsUnit` instance comes through `UnitPlace`.
   - For a program, C is `Prog.circuit`: the pinned rows the verifier parses, one `Op.row` per computed row.
   - L1 (each template's rows compute its gates) is named and tested, in ASSUMPTIONS §1.5.
   - I cite this in ASSUMPTIONS §9 and DESIGN §12.
2. **The decoder patch is in #145**, not #133, and applied unchanged to the one-table `FlockCompiled.lean`. The only
   edit is `simp only [hu, ↓reduceDIte]` in place of the deprecated `dif_pos`.
3. **`Op`:** I haven't touched it, and won't. `Op.row` stays in #144.

## How #141 is wired (`Audit/FlockBatched.lean`)

It follows your recipe, restated in #133's joint form:
- **The session.** `batchedSession S R` is `(sessionB execArith H E (plan S R)).map (decide ∘ acceptedB)`, with
  `plan : Finset (Fin n) → Reg → List (TabSpec mPts)`, `tab S R u` for the unit's table, and a decoder per drawn unit
  (`DecoderB`, over messages of the shape of `tabOf S R u`).
- **`ks` and `link`.** `ks` is `prob (acceptedB …) (sessionB …) τ₀ * ofReal (failProbB … (tab S R u) Kr τ₀)`. `link` is
  the same with `extractProbB … (LinkEvB … u X)`, where `LinkEvB` is your predicate form of the link event.
- **`cover`** is `le_mul_of_one_le_right` with `one_le_fail_add_B'`. `hG` comes from `LoweringSoundB`, the per-table
  lowering.
- **ε_ks** is `ksAvgB`: the average over the draw of `⨆ j, ofReal (ksBoundB … j Kr τ₀)`, using `joint_le_B'` and `le_iSup`.
  It is `flock_batched_knowledgeSound`.
- **The lowering:** `loweringSoundB_of_place (place : ∀ S R u, u ∈ S → UnitPlace P (tabOf S R u).S u)`.
- **For your link theorem,** the statement to prove is `(P.analysisB H E plan tab decode Xc Kr hlow).LinkSound δlink`. Its
  event is `LinkEvB` on the extracted table: committed, and every close satisfying candidate's reading of `u` differs
  from `X` on `u`'s wires.

**`batch`:** `Audit/Flock.lean` now uses your `Game.batch`, and `Audit.batch` is gone.
