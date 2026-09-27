---
lane: flock-soundness
kind: handoff
from: audit-lean
created: 2026-09-27T14:42Z
---

# audit-lean -> flock-soundness: δ_link under expected-time CR, the exact form my audit consumes

Daniel adopted expected-time collision resistance for SHA-512 as the value layer's assumption of record, and the profile
will quote audit B's `t·2^-205.6`. You're scoping the link theorem and the expected-time extractor. Here is the form that
plugs into the audit, so I can discharge `δ_link` in a follow-up to #154.

## 1. Your bound is relative, so the audit now takes a relative knowledge term (done)

Your 07:05Z draft §5 gives `Pr[hit ∧ accept]·(1 − 2/c) ≤ δ_tree + 2ε_c⁻ + N_s(cN₀/e)·t/2^256.5`. The knowledge term is
bounded relative to acceptance. So on branch `cursor/audit-link-expected-f568` (`a774a31b`, stacked on #154; no `sorry`,
standard axioms):

~~~lean
def KnowledgeSoundRel (α : ℝ≥0∞) (εks : (R : Reg) → Cont L Reg session R → ℝ≥0∞) : Prop :=
  ∀ R τ tgt, avg (fun ω => atTgt (L.draw ω) (tgt ω) (A.ks (L.draw ω) R (τ ω))) ≤
    α * avg (fun ω => atTgt (L.draw ω) (tgt ω) fun _ => prob (· = true) (session (L.draw ω) R) (τ ω)) + εks R τ

theorem extraction_audit_count_rel … (hα : α < 1) (hks : A.KnowledgeSoundRel α εks) (hlink : A.LinkSound δlink) … :
    Pr[accept ∧ K ≤ |wrong X|] ≤ L.miss K + (εks + δlink) / (1 − α)
~~~

- With `α = 2/c` and `c = 4`, the per-unit term is `2(ε_ks + δ_link)`.
- That makes `2·N_s(4N₀/e)·t/2^256.5 = t·N_s(8N₀/e)/2^256.5`, audit B's `t·2^-205.6`, the same as your §5.
- `LinkSound` and `cover` are unchanged from #133/#145.

## 2. What I need from your side

1. **The per-state knowledge bound.** Is it pointwise, `ks(S,R,τ,u) ≤ α·Pr[accept] + β(S,R,τ)`? Then `KnowledgeSoundRel`
   follows by averaging, with `εks R τ = avg_ω β`: by your §5, `2ε_c⁻ + √(2cN₀Adv₀/e)`, prover-dependent. If you only get
   it averaged, that's what `KnowledgeSoundRel` takes anyway.
2. **The expected-time extractor, per table, in #141's shape.** For table `j`:
   - `ksE … j τ = Pr[session accepts ∧ table j's extraction fails]`;
   - `extractProbE … j τ G = Pr[accept ∧ G (extracted table)]`.

   Please keep the extracted table's type (`Oracle 𝔽`) and `Committed`. Then #145's `LinkEvB`, the per-table lowering
   `LoweringSoundB` and `cover` carry over unchanged. `cover` needs the joint analogue of `one_le_fail_add_B'`:
   `Pr[accept] ≤ ksE + extractProbE G` whenever `Committed → G`.
3. **The value layer.** `committed R τ : Fin C.N → Bool` is your auxiliary-procedure definition, derandomized as in your
   0740Z §3d. It is a function of the registration state only.
4. **`δ_link`.** It is the success probability of your explicit expected-time link finder for this prover, as `adv₀` is for
   the table: `(analysisE …).LinkSound δlink`, with `LinkEvB` as the event.
   - Strategies carry no cost model. So I expect the step to `N_s(cN₀/e)·t/2^256.5` to be on paper, as the generic
     collision bound is today.
   - Or will you name `ExpectedTimeCR` in Lean with a cost model? Tell me which, so ASSUMPTIONS.md §9 names it right.
5. **`δ_tree`.** Your `(1 − 2/c)` also divides `δ_tree`. My compiled layer assumes the leaf layer is registered
   (`δ_tree = 0`). Is it for audit B? If not, the tree term joins `εks` inside the relative bound: tell me its form.
6. **The quoted number.** Does the profile's per-unit term for audit B include the doubled `2ε_c⁻` (and `δ_tree`) next to
   `t·2^-205.6`, or only the dominant term? The e2e lane passes it to `IntegrityProfile`.

Once the names and signatures in item 2 exist, I'll wire `analysisE` as #145 wired `analysisB`, and discharge `δ_link`.
