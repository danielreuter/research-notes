---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: draft · status: decided (option 1, Daniel 09:19), done in
[PR #144](https://github.com/danielreuter/verity/pull/144) · repo: danielreuter/verity ·
re: #133's `LoweringSoundC` (the compiled lowering), for the RoPE template

# The compiled lowering for RoPE: what it takes

**The ask.** Prove #133's `LoweringSoundC` for the RoPE template: a message packing a witness that satisfies the
table's statement decodes to values on which every drawn unit is correct (`Partition.Correct`, relative to the audit's
Boolean circuit `C`).

**What the unit is**, measured with the repo's lowering (`REG.module("rope-head").lowering(TM.subcircuit("rope-head",
D=64))`):

- `rope-head/neox-bf16/pair` is one `flock-ir-unit/v2` unit of rows per pair `(x[i], x[i+D/2], cos[i], sin[i])`. That is
  4 × 16 input bits and 2 × 16 output bits, the same for every `D`.
- It has **6,273 useful rows**, and each row is `z_i = (⊕_{c∈A_i} z_c)·(⊕_{c∈B_i} z_c)` over GF(2).
  - The row shapes `(|A|, |B|)` are mostly (1,1) (631), (2,1) (276), (1,8) (192), (1,4) (178) and (3,3) (166). So the
    rows are not one binary gate each.
- The Lean verifier doesn't lower gates. It parses the rows (`Flock/Net.lean`) and checks them. The rows come from the
  Python IR lowering (`verity_flock.ir_lower`, piece by piece from the IR's bf16 primitives), not from `boolean_export`.

**So the statement depends on what `C` is.** It is abstract in #133.

1. **`C` is read off the pinned rows:** each row expands into XOR trees and one AND, and the units are the pinned
   files' units.
   - Then the lowering is generic and provable now. Satisfied rows at a unit's place in a block give the row circuit
     on the decoded bits, provided the rows are topologically ordered.
   - Two lemmas: the rows define a function of the unit's inputs, and the decoder reads the unit's committed wires
     from the block layout (`Statement.block`, §16.5's unit range).
   - About 300 lines, with no per-template proof. RoPE is an instance, plus a kernel check that its pinned rows are
     ordered.
   - The claim "the pinned unit computes the IR's bf16 RoPE pair" then sits outside the audit's soundness, as a
     property of `C`. Today it rests on the IR comparison tests (`test_rope_unit_matches_its_primitives`, and a
     mutated row is caught).
2. **`C` is `boolean_export`'s circuit for RoPE.** Then the lowering is a functional equivalence of two circuits on
   64 input bits.
   - The kernel can't enumerate `2^64`, and `native_decide` is out.
   - It needs a per-piece proof (bf16 multiply and add gadgets against a Lean bf16 model), or certificates. For
     example, a row-by-row mapping to gate values, checked by the kernel on the 6k rows.
   - That is a research-sized item per template.

**Recommendation.** Take (1) for the audit's compiled instance. It makes `LoweringSoundC` a theorem for every
template, not just RoPE. Keep "the rows compute the IR's function" as a separately stated property of `C`, with the
tests as its evidence until a proof route exists. The choice is shared with audit-lean (it fixes `C` and the decoder) and
with level 3 (it moves the claim that the rows compute the IR), so I'm not starting it before they agree.

**Still needed in either case:** the table statement's layout in the model. That is where a unit's rows and committed
wires sit among the BLAKE3 row-leaf runs, lookup slots and Δ copies of §16.5, in the level-0 message that
`witnessOf` unpacks.

**Update 09:57Z.** Daniel took option 1 at 09:19, and it is now [PR #144](https://github.com/danielreuter/verity/pull/144).
- A row is one gate (`Op.row`), and the lowering is proved for every template (`lowering_sound`, `UnitPlace.correct`).
- The rows computing the IR's function is L1, a named hypothesis in ASSUMPTIONS.md §1.5.
- The table statement's layout is stated as a hypothesis, `Placement`, which the statement builder must meet at level 3.
