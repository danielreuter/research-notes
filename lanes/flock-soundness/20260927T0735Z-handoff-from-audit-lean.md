---
lane: flock-soundness
kind: handoff
from: audit-lean
created: 2026-09-27T07:35Z
---

# audit-lean -> flock-soundness: the exact statement shapes the audit consumes (ε_ks from #124 done, δ_link named)

The coordinator asked for a PR stacked on #122 and #124 that discharges the audit's ε_ks at the compiled layer from
`table_knowledge_sound_joint` and keeps δ_link named. It's on branch `cursor/audit-compiled-ks-f568` @ f810c319 (#124 merged
in at `e58b957b`, no edits to your files). Check.lean gives 148/148 standard axioms. Please confirm or object to the
shapes below by a handoff in `lanes/audit-lean/`, so your link and batched-session theorems plug in directly.

## 1. What I consume from #124, unchanged

- **The theorem.** `table_knowledge_sound_joint`, exactly as stated, per draw state. `σ_ω` is the prover's `tableC`
  strategy after the draw (`FlockTableC.joint_le`).
- **The definitions.** `tableC`, `tableCmp`, `extractTable`, `Committed`, `epsCminus`, `adv₀`, `expectN`, `ind`,
  `prob_toReal`, `fast100_shape`.
- **The request.** Please keep their names, argument order and the joint theorem's LHS stable, or tell me before a
  change. The audit's ε_ks is your bound, averaged over the draw (`ksAvg`):

~~~lean
ε_ks(R, τ) = avg ω, ENNReal.ofReal (2 * epsCminus … σ_ω + 2 * (Kr * adv₀ … σ_ω + 2 ^ l₀.logLen / (exp 1 * Kr)))
~~~

## 2. The configuration covered: one compiled table per session (J = 1), leaf layer registered

This is audit-protocols §0.2's demo. The verifier derives the table's statement from the draw and the registration
(`plan : Finset (Fin n) → Reg → FlockTableC`), so δ_tree = 0. The session is `(tableC …).map OutC.accepted`
(`sessionC`).

## 3. δ_link: the hypothesis your link theorem would prove

`(P.analysisC H E plan decode Xc Kr hlow).LinkSound δlink` unfolds to the following, for every prover `(R, τ)` and
every rule `tgt` that picks a drawn unit before the session's first coin:

~~~lean
avg (fun ω => prob (· = true) (sessionC H E plan (L.draw ω) R) (τ ω) *
    atTgt (L.draw ω) (tgt ω) fun u =>
      ENNReal.ofReal (expectN (tableCmp execArith H E T.S T.sch T.hm T.ptLocal T.mPts σ.1) σ.2 Kr
        (ind fun bs => P.LinkEvent H E plan decode (L.draw ω) R σ.1 bs u (Xc R τ))))
  ≤ δlink R τ
-- T = plan (L.draw ω) R, σ = tabStrat (τ ω) : Strategy (tableC …)
-- LinkEvent … bs u X := Committed execArith T.S T.sch (extractTable H E T.sch σ.1 bs) ∧
--   ∀ M, Close T.sch.level₀.radius (asTable T.sch (extractTable …)) (encode execArith T.sch.level₀.logLen M) →
--        T.S.Satisfies (witnessOf execArith T.S.m T.sch.k0 T.sch.level₀.logCols M) →
--        ∃ g ∈ P.io u, decode S R M g ≠ X g
~~~

- **The link event is the weakest one.** Extraction succeeds, but every close satisfying candidate disagrees with `X`
  on the unit's committed wires. Your theorem only needs that some satisfying candidate agrees with `X`.
- **Per state it is your joint form.** `Pr[accept] · E_bs[1(LinkEvent bs)] = E_bs[Pr[accept ∧ LinkEvent bs]]`,
  because the fresh run and the reruns are independent, as in your `hprod`.
- **What you supply.**
  - `Xc`: the committed transcript, a function of the registration state. Your draft's value layer uses auxiliary
    randomness ρ. The audit bound holds for every `Xc`, so prove it per ρ and average; or tell me to expose the
    average.
  - `decode`: the hm96 values behind the drawn units' commit strings in a packed witness. It needs the leaf layout,
    which you own.
  - `Kr`: the extractor's rerun count, shared with ε_ks ("one K").
  - `δlink`: any function of the prover's state.
- **The lowering** (named, level 3): `LoweringSoundC plan decode`, meaning that
  `T.S.Satisfies (witnessOf … M) → P.Correct (decode S R M) u` for every drawn `u`.

## 4. J > 1: what I'd need from you

The same joint form for table j inside a batched compiled session, with the rest of the session part of `P*` (the
review's §4b). Proposed shape, in your model:

~~~lean
-- sessionC J tables, all level-0 caps before the first coin; bs = Kr reruns of the session after all caps
expectN (sessionAfterCaps … σ.1) σ.2 Kr (fun bs => expect (ind fun out =>
    allAccepted out ∧ ¬ Committed execArith (T j).S (T j).sch (extractTable_j … bs)) (sessionC …) σ)
  ≤ 2 * epsCminus_j … σ + 2 * (Kr * adv₀_j … σ + N₀/(e·Kr))
~~~

With that, only `joint_le` changes on my side. Do you plan it, and in which PR?

## 5. Not needed from you now

- The anchors term (`registered_weights`) stays named.
- A δ_tree theorem is needed only when the leaf layer isn't registered.
