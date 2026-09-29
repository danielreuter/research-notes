import FlockSoundness.Game.Prob

/-!
# Named assumptions of the γ step (design note §12.2, A8 to A11)

None of these is used by the accountable-compute theorems (§12.2 (2), (2′)). They are the hypotheses of the γ step
(`compute_used`, §12.2 (3)), stated over any game whose outcomes carry the verdict, the committed transcript's
verified work and the prover's online cost.

* `AnchoredInputs` (**A9**, §2.3's R5): the audit accepts while the committed salt, forward index or weights that the
  X and Y units read differ from their registration anchors with probability at most `δin`. It is `main`'s
  `Partition.AnchorsSound` in event form: the input unit, proved on every audit.
* `UniqueCallIndices` (**A11**, X-SPC-18): the audit accepts a transcript that registers a call index twice with
  probability at most `δidx`; the verifier's refusal at registration makes it 0.
* `PerTileCount` (**A8, with A10**; not proved: PoUW's per-tile count statement, §8 item 13): on transcripts whose
  inputs are anchored and whose call indices are unique, except with probability `ηTT + εcr`, the online cost is at
  least `(1 − γ)` times the verified work. **A10, the key's named hash assumptions**, enter here: the statement is in
  the random-oracle model (`random-oracle`: the Program's SHA-512 and SHAKE256 stand in for TT_NCP_U's oracle), and
  `εcr` is the collision term of `cr/sha-512` for D_s and the node hashes (about `q²/2^257` for digests of at least
  256 bits). PoUW's Lean states TT_NCP_U per call, not per tile, so this stays a hypothesis.

`main`'s own named hypotheses, `Analysis.KnowledgeSound ε_ks` and `Analysis.LinkSound δ_link`
(`FlockSoundness.Audit.OneStage`), are the proof system's per-unit error, the design note's `ε_proof = ε_ks + δ_link`.
-/

namespace PouwAccountable

open FlockSoundness FlockSoundness.Game
open scoped ENNReal

/-- **A9, anchored inputs**: an accepted outcome has inputs other than the registration anchors with probability at
most `δin`. -/
def AnchoredInputs {α : Type} (g : Game α) (s : Strategy g) (accept anchored : α → Prop) (δin : ℝ≥0∞) : Prop :=
  prob (fun o => accept o ∧ ¬ anchored o) g s ≤ δin

/-- **A11, no call index registered twice**: an accepted outcome repeats a call index with probability at most
`δidx`. -/
def UniqueCallIndices {α : Type} (g : Game α) (s : Strategy g) (accept unique : α → Prop) (δidx : ℝ≥0∞) : Prop :=
  prob (fun o => accept o ∧ ¬ unique o) g s ≤ δidx

/-- **A8 with A10, PoUW's per-tile count statement**: on outcomes with anchored inputs and unique call indices, the
online cost `cost` falls below `(1 − γ)` times the verified work `verified` with probability at most `ηTT + εcr`
(TT_NCP_U's error `ε(q, N)` per tile, and the collision term of `cr/sha-512`, in the random-oracle model). -/
def PerTileCount {α : Type} (g : Game α) (s : Strategy g) (anchored unique : α → Prop) (cost verified : α → ℝ)
    (γ : ℝ) (ηTT εcr : ℝ≥0∞) : Prop :=
  prob (fun o => anchored o ∧ unique o ∧ cost o < (1 - γ) * verified o) g s ≤ ηTT + εcr

end PouwAccountable
