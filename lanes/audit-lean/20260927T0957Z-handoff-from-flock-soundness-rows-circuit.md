---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open · repo: danielreuter/verity ·
[PR #144](https://github.com/danielreuter/verity/pull/144) (branch `cursor/flock-lowering-8569`, head `084f8478`,
stacked on #141)

# The audit's circuit C is the rows the verifier parses: its definition, and the decoder per drawn unit

Daniel decided at 09:19 to take option 1:
- define #133's circuit C as the pinned rows the verifier parses;
- prove the generic lowering for every template;
- name "each template's rows compute its gates" as a hypothesis, L1.

The lowering is your hypothesis, so please agree C's definition with me. Everything below is in #144, with no `sorry` and
standard axioms (159 of 159).

## C

- **One gate more, in #122's `Audit/Circuit.lean`:** `Op.row (a b : List (Fin N))`.
  - Its value is `xorSum a v && xorSum b v`, and `args = a ++ b`.
  - A computed row of a pinned unit is one such gate.
- **A template's unit is `Rows`** (`Lowering.lean`).
  - It has `nIn` input columns, then `nComp` computed rows, then the constant as the last column.
  - Row `i` reads earlier columns or the constant (`topo`).
- **A unit is an instance of `R`** (`Partition.IsRowsUnit u R`):
  - `wire : Fin R.w → Fin C.N` is injective;
  - the unit's gates are exactly `wire (R.comp i)`, each `Op.row ((R.a i).map wire) ((R.b i).map wire)`;
  - its input columns and its constant are wires outside the unit.
- **In the audit, C stays abstract**, as in #133 now. The lowering needs only an `IsRowsUnit` instance for each drawn
  unit, and `UnitPlace` carries it.
- **For a program, C is `Prog.circuit`.** A `Prog` is its inputs, then units appended one at a time, each with its
  input columns and its constant wired to earlier gates. `Prog.isRowsUnit` gives every unit's instance:
  `Nonempty ((p.partition outs).IsRowsUnit u (p.rows u))`.
- **The constant** is a gate that the unit reads. `Placement` records that the constant's rows read the pin, so a
  decoded transcript carries `true` there (`UnitPlace.decode_one`).

## The lowering

- `pl : UnitPlace P S u` holds a drawn unit's rows, its instance, its block `o` and its columns `col`, with
  `Placement S R col`.
- **`UnitPlace.correct` (`lowering_sound`):** every witness that satisfies `S` decodes, as `pl.decode z`, to a transcript
  on which `u` is correct.

## One change in #133: the decoder per drawn unit

One decoder cannot, in general, make two drawn units that share a wire both correct. Each unit holds that wire in its own
columns, and only hm96 binding (the link) makes the two agree. Here is the patch against `6d4e28c0`:

~~~diff
diff --git a/backends/flock/verifier/lean/soundness/FlockSoundness/Audit/FlockCompiled.lean b/backends/flock/verifier/lean/soundness/FlockSoundness/Audit/FlockCompiled.lean
index 058041e9..9d5834d8 100644
--- a/backends/flock/verifier/lean/soundness/FlockSoundness/Audit/FlockCompiled.lean
+++ b/backends/flock/verifier/lean/soundness/FlockSoundness/Audit/FlockCompiled.lean
@@ -1,6 +1,7 @@
 import FlockSoundness.Audit.Extraction
 import FlockSoundness.Audit.Flock
 import FlockSoundness.Knowledge
+import FlockSoundness.Lowering
 
 /-!
 # The Flock audit at the compiled layer: `ε_ks` from `table_knowledge_sound_joint`
@@ -111,9 +112,9 @@ noncomputable def tabStrat {S : Finset (Fin n)} {R : Reg} (τ : Strategy (sessio
     Strategy ((plan S R).game H E) :=
   Strategy.ofMap _ _ τ
 
-/-- A decoder: the values behind the drawn units' commit strings that a level-0 message of the
-table packs (the `hm96` openings in the witness). -/
-abbrev Decoder := (S : Finset (Fin n)) → (R : Reg) →
+/-- A decoder: for each drawn unit, the values a level-0 message of the table packs for it. Two
+drawn units that share a wire hold it in different columns, so each has its own reading. -/
+abbrev Decoder := (S : Finset (Fin n)) → (R : Reg) → Fin n →
   Message 𝔽 (plan S R).sch.k0 (plan S R).sch.level₀.logCols → (Fin C.N → Bool)
 
 /-- **The lowering, compiled** (named hypothesis): a message packing a witness that satisfies the
@@ -121,7 +122,7 @@ table's statement decodes to values on which every drawn unit is correct. -/
 def LoweringSoundC (decode : Decoder (C := C) (Reg := Reg) plan) : Prop :=
   ∀ S R u, u ∈ S → ∀ M, (plan S R).S.Satisfies
     (witnessOf execArith (plan S R).S.m (plan S R).sch.k0 (plan S R).sch.level₀.logCols M) →
-    P.Correct (decode S R M) u
+    P.Correct (decode S R u M) u
 
 /-- **The link event** on the extractor's reruns `bs`: the extracted table is committed, but every
 close message packing a satisfying witness decodes, on `u`'s committed wires, to values other than
@@ -135,7 +136,18 @@ def LinkEvent (decode : Decoder (C := C) (Reg := Reg) plan) (S : Finset (Fin n))
         (encode execArith (plan S R).sch.level₀.logLen M) →
       (plan S R).S.Satisfies
         (witnessOf execArith (plan S R).S.m (plan S R).sch.k0 (plan S R).sch.level₀.logCols M) →
-      ∃ g ∈ P.io u, decode S R M g ≠ Xc g
+      ∃ g ∈ P.io u, decode S R u M g ≠ Xc g
+
+/-- **The lowering from the drawn units' places** (`Lowering.lean`): if every drawn unit has a place
+in its table, reading each unit from its block discharges `LoweringSoundC`. -/
+theorem loweringSoundC_of_place (place : ∀ S R u, u ∈ S → UnitPlace P (plan S R).S u) :
+    P.LoweringSoundC plan fun S R u M =>
+      if h : u ∈ S then (place S R u h).decode
+        (witnessOf execArith (plan S R).S.m (plan S R).sch.k0 (plan S R).sch.level₀.logCols M)
+      else fun _ => false := by
+  intro S R u hu M hM
+  simp only [dif_pos hu]
+  exact (place S R u hu).correct hM
 
 open Classical in
 /-- **Accept and the link fails**, jointly over the fresh run and the extractor's `Kr` reruns. -/
~~~

- **Checked on a local merge** of #144 with #133 at `6d4e28c0`, with this patch applied and
  `#print axioms FlockSoundness.Audit.Partition.loweringSoundC_of_place` added to `Check.lean`.
  - It builds, and all 171 axiom checks are standard.
  - The merge conflicts only in `FlockSoundness.lean`'s imports and in `Check.lean`. Take both sides.
- **`analysisC`'s `cover` proof is unchanged.** `hlow S R u hS M hsat` is now about `decode S R u M`.
- **The link event becomes per unit too.** That is what the link theorem proves: some satisfying candidate's reading of
  `u` agrees with `X` on `u`'s wires.
- **With several tables (#141)**, `place S R u` is a `UnitPlace` for the statement of `u`'s table, `tab S R u`.

## What stays named

- **`Placement` for the executable's statement**, the slots with Δ XORed in (PROTOCOL.md §16.1). That is the statement
  builder's job, at level 3.
  - The parser checks the pinned files' input rows and constant.
  - `test_pinned_rows_read_earlier_columns` checks the rest of the shape `Rows` needs: every computed row reads only
    earlier columns or the constant, and never an input padding column.
- **L1** (ASSUMPTIONS.md §1.5): each template's rows compute its gates, in the program's Boolean circuit.
  - Its evidence is the IR comparison tests.
  - The path to discharge it is a verified lowering, V[B] generated in Lean with an equivalence proof.

## Asks

1. Is C as above right for #133: abstract in the audit, `IsRowsUnit` through `UnitPlace`, and `Prog.circuit` for a
   program?
2. Will the decoder patch go into #133 or into your several-table follow-up? I won't touch `FlockCompiled.lean`.
3. Please don't edit `Op` in parallel. If you'd rather `Op.row` live in #122 or #133, say so and I'll rebase #144 onto
   it.
